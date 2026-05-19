import json
import logging
import random
import time
from typing import Any, Dict, Generator, List, Optional, Union

from openai import OpenAI
from openai import APIError, RateLimitError as OpenAIRateLimitError, APITimeoutError

from config import Config
from .data_profiler import DataProfile
from .prompt_templates import (
    SYSTEM_PROMPT,
    QUERY_SYSTEM_PROMPT,
    get_overview_prompt,
    get_insight_prompt,
    get_query_prompt,
)

logger = logging.getLogger(__name__)


class AIAnalyzerError(Exception):
    pass


class NetworkError(AIAnalyzerError):
    pass


class RateLimitError(AIAnalyzerError):
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class APIError(AIAnalyzerError):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class ResponseParseError(AIAnalyzerError):
    pass


class AIAnalyzer:
    SYSTEM_PROMPT = SYSTEM_PROMPT
    QUERY_SYSTEM_PROMPT = QUERY_SYSTEM_PROMPT

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        self.base_url = base_url or Config.DEEPSEEK_BASE_URL
        self.model = model or Config.DEEPSEEK_MODEL
        self.timeout = timeout or Config.API_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else Config.API_MAX_RETRIES

        self._validate_config()
        self._init_client()

    def _validate_config(self) -> None:
        if not self.api_key:
            raise AIAnalyzerError(
                "未配置DeepSeek API密钥。请设置环境变量 DEEPSEEK_API_KEY 或在初始化时传入 api_key 参数。"
            )

    def _init_client(self) -> None:
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0,
        )

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _log_request(self, payload: Dict[str, Any]) -> None:
        log_payload = {k: v for k, v in payload.items() if k != "messages"}
        log_payload["messages_count"] = len(payload.get("messages", []))
        logger.info("API请求 -> %s | 参数: %s", self.model, json.dumps(log_payload, ensure_ascii=False))

    def _log_response(self, usage: Optional[Dict[str, int]] = None) -> None:
        logger.info("API响应 | Token用量: %s", usage or "流式响应")

    def _log_error(self, error: Exception, attempt: int) -> None:
        logger.warning("API请求失败 (第%d次尝试): %s - %s", attempt, type(error).__name__, error)

    def _format_profile(self, profile: DataProfile) -> str:
        lines = []
        lines.append(f"数据规模: {profile.row_count} 行 × {profile.column_count} 列")
        lines.append("")

        if profile.warnings:
            lines.append("数据质量警告:")
            for warning in profile.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        lines.append("各列详情:")
        for col in profile.columns:
            lines.append(f"  [{col.name}]")
            lines.append(f"    类型: {col.dtype}")
            lines.append(f"    非空值: {col.non_null_count} | 缺失值: {col.null_count} ({col.null_ratio:.1%})")

            if col.stats:
                if 'mean' in col.stats and col.stats['mean'] is not None:
                    lines.append(f"    均值: {col.stats['mean']} | 中位数: {col.stats['median']}")
                    lines.append(f"    标准差: {col.stats['std']} | 范围: [{col.stats['min']}, {col.stats['max']}]")
                    lines.append(f"    四分位: Q1={col.stats['q25']} | Q3={col.stats['q75']}")
                if 'unique_count' in col.stats:
                    lines.append(f"    唯一值数量: {col.stats['unique_count']}")
                if 'top_values' in col.stats and col.stats['top_values']:
                    top_str = ", ".join(
                        f"{v['value']}({v['count']}次)" for v in col.stats['top_values'][:5]
                    )
                    lines.append(f"    最常见的值: {top_str}")

        return '\n'.join(lines)

    def _format_sample(self, sample_data: str) -> str:
        return sample_data if sample_data else "(无样本数据)"

    def _build_messages(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt or self.SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def _build_extra_body(self) -> Dict[str, Any]:
        extra_body = {}
        if self.model == "deepseek-v4-pro":
            extra_body = {
                "thinking": {"type": "enabled"},
                "reasoning_effort": "high",
            }
        return extra_body

    def _stream_response(
        self, stream
    ) -> Generator[str, None, None]:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _make_request(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Union[Dict[str, Any], Generator[str, None, None]]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        extra_body = self._build_extra_body()
        if extra_body:
            payload["extra_body"] = extra_body

        self._log_request(payload)

        try:
            if stream:
                stream_response = self.client.chat.completions.create(**payload)
                self._log_response()
                return self._stream_response(stream_response)
            else:
                response = self.client.chat.completions.create(**payload)
                self._log_response(response.usage.model_dump() if response.usage else None)
                return response.choices[0].message.content

        except OpenAIRateLimitError as e:
            raise RateLimitError(
                "API请求频率超限，请稍后重试",
                retry_after=None,
            )
        except APITimeoutError as e:
            raise NetworkError(f"请求超时({self.timeout}秒): {e}")
        except APIError as e:
            if e.status_code == 401:
                raise APIError("API密钥无效或已过期，请检查配置", status_code=401)
            elif e.status_code == 429:
                raise RateLimitError("API请求频率超限，请稍后重试", retry_after=None)
            else:
                error_msg = str(e)
                if hasattr(e, 'body') and e.body:
                    try:
                        error_body = json.loads(e.body)
                        error_msg = error_body.get("error", {}).get("message", error_msg)
                    except:
                        pass
                raise APIError(
                    f"API请求失败 (HTTP {e.status_code}): {error_msg}",
                    status_code=e.status_code,
                )
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                raise APIError("API密钥无效或已过期，请检查配置", status_code=401)
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                raise NetworkError(f"请求超时({self.timeout}秒): {e}")
            else:
                raise NetworkError(f"网络请求异常: {e}")

    def _make_request_with_retry(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Union[str, Generator[str, None, None]]:
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._make_request(
                    messages, stream=stream, temperature=temperature, max_tokens=max_tokens
                )
                return result

            except RateLimitError as e:
                last_exception = e
                self._log_error(e, attempt)
                if attempt < self.max_retries:
                    wait_time = e.retry_after if e.retry_after else (2 ** attempt + random.uniform(0, 1))
                    logger.info("等待 %.1f 秒后重试...", wait_time)
                    time.sleep(wait_time)

            except (NetworkError, APIError) as e:
                last_exception = e
                self._log_error(e, attempt)
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logger.info("等待 %.1f 秒后重试...", wait_time)
                    time.sleep(wait_time)

            except ResponseParseError:
                raise

        raise last_exception

    def analyze_data_overview(
        self,
        profile: DataProfile,
        sample_data: Optional[str] = None,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        profile_text = self._format_profile(profile)
        sample_text = self._format_sample(sample_data or "")

        user_prompt = get_overview_prompt(
            profile_text=profile_text,
            data_sample=sample_text,
        )

        messages = self._build_messages(user_prompt)
        return self._make_request_with_retry(messages, stream=stream)

    def analyze_insights(
        self,
        profile: DataProfile,
        sample_data: Optional[str] = None,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        profile_text = self._format_profile(profile)
        sample_text = self._format_sample(sample_data or "")

        user_prompt = get_insight_prompt(
            profile_text=profile_text,
            data_sample=sample_text,
        )

        messages = self._build_messages(user_prompt)
        return self._make_request_with_retry(messages, stream=stream)

    def query(
        self,
        question: str,
        profile: DataProfile,
        sample_data: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        if not question or not question.strip():
            raise AIAnalyzerError("问题不能为空")

        profile_text = self._format_profile(profile)
        sample_text = self._format_sample(sample_data or "")

        user_prompt = get_query_prompt(
            profile_text=profile_text,
            data_sample=sample_text,
            question=question.strip(),
        )

        messages = self._build_messages(
            user_prompt,
            system_prompt=self.QUERY_SYSTEM_PROMPT,
            history=history,
        )
        return self._make_request_with_retry(messages, stream=stream)

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
