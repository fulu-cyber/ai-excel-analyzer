import logging
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MissingValueStrategy(str, Enum):
    FILL_MEAN = "mean"
    FILL_MEDIAN = "median"
    FILL_MODE = "mode"
    FILL_VALUE = "value"
    FILL_FFILL = "ffill"
    FILL_BFILL = "bfill"
    DROP_ROW = "drop_row"
    DROP_COLUMN = "drop_column"
    MARK = "mark"


class OutlierMethod(str, Enum):
    IQR = "iqr"
    ZSCORE = "zscore"


class OutlierAction(str, Enum):
    REMOVE = "remove"
    CAP = "cap"
    MARK = "mark"
    MEDIAN = "median"
    MEAN = "mean"


class NormalizeMethod(str, Enum):
    MINMAX = "minmax"
    ZSCORE = "zscore"
    MAXABS = "maxabs"


@dataclass
class SnapshotStats:
    row_count: int
    column_count: int
    null_counts: Dict[str, int]
    null_ratios: Dict[str, float]
    duplicate_count: int
    dtypes: Dict[str, str]


@dataclass
class ProcessingResult:
    success: bool
    message: str
    rows_affected: int = 0
    columns_affected: int = 0
    before_stats: Optional[SnapshotStats] = None
    after_stats: Optional[SnapshotStats] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks_passed: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationRule:
    column: str
    rule_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class DataProcessor:
    NUMERIC_TYPES = {
        "int16", "int32", "int64",
        "float16", "float32", "float64",
        "uint8", "uint16", "uint32", "uint64",
    }

    def __init__(self, df: pd.DataFrame, copy: bool = True):
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"输入必须是pandas DataFrame，收到: {type(df).__name__}")
        self._original = df.copy() if copy else df
        self.df = df.copy() if copy else df
        self._history: List[ProcessingResult] = []

    @property
    def original(self) -> pd.DataFrame:
        return self._original

    @property
    def history(self) -> List[ProcessingResult]:
        return list(self._history)

    def _take_snapshot(self, df: pd.DataFrame) -> SnapshotStats:
        null_counts = {col: int(df[col].isnull().sum()) for col in df.columns}
        total = len(df)
        null_ratios = {
            col: round(cnt / total, 4) if total > 0 else 0.0
            for col, cnt in null_counts.items()
        }
        return SnapshotStats(
            row_count=len(df),
            column_count=len(df.columns),
            null_counts=null_counts,
            null_ratios=null_ratios,
            duplicate_count=int(df.duplicated().sum()),
            dtypes={col: str(df[col].dtype) for col in df.columns},
        )

    def _record(self, result: ProcessingResult) -> ProcessingResult:
        self._history.append(result)
        return result

    def _is_numeric(self, series: pd.Series) -> bool:
        return series.dtype.name in self.NUMERIC_TYPES

    def _get_numeric_columns(self, columns: Optional[List[str]] = None) -> List[str]:
        target = columns if columns else list(self.df.columns)
        return [c for c in target if c in self.df.columns and self._is_numeric(self.df[c])]

    def reset(self) -> None:
        self.df = self._original.copy()
        self._history.clear()

    def get_snapshot(self) -> SnapshotStats:
        return self._take_snapshot(self.df)

    def compare_stats(self) -> Dict[str, Any]:
        before = self._take_snapshot(self._original)
        after = self._take_snapshot(self.df)

        null_change = {}
        for col in set(before.null_counts) | set(after.null_counts):
            b = before.null_counts.get(col, 0)
            a = after.null_counts.get(col, 0)
            if b != a:
                null_change[col] = {"before": b, "after": a, "diff": a - b}

        return {
            "before": before,
            "after": after,
            "row_change": after.row_count - before.row_count,
            "column_change": after.column_count - before.column_count,
            "duplicate_change": after.duplicate_count - before.duplicate_count,
            "null_change": null_change,
            "operations_count": len(self._history),
        }

    def format_comparison_report(self) -> str:
        comp = self.compare_stats()
        before: SnapshotStats = comp["before"]
        after: SnapshotStats = comp["after"]

        lines = [
            "=" * 60,
            "数据处理对比报告",
            "=" * 60,
            "",
            f"处理操作次数: {comp['operations_count']}",
            "",
            "-" * 40,
            "维度变化:",
            f"  行数: {before.row_count} -> {after.row_count} ({comp['row_change']:+d})",
            f"  列数: {before.column_count} -> {after.column_count} ({comp['column_change']:+d})",
            f"  重复行: {before.duplicate_count} -> {after.duplicate_count} ({comp['duplicate_change']:+d})",
            "",
        ]

        if comp["null_change"]:
            lines.append("-" * 40)
            lines.append("缺失值变化:")
            for col, change in comp["null_change"].items():
                lines.append(
                    f"  {col}: {change['before']} -> {change['after']} ({change['diff']:+d})"
                )
            lines.append("")

        dtype_changes = {
            col: {"before": before.dtypes[col], "after": after.dtypes[col]}
            for col in before.dtypes
            if col in after.dtypes and before.dtypes[col] != after.dtypes[col]
        }
        if dtype_changes:
            lines.append("-" * 40)
            lines.append("类型变化:")
            for col, change in dtype_changes.items():
                lines.append(f"  {col}: {change['before']} -> {change['after']}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def handle_missing_values(
        self,
        strategy: Union[str, MissingValueStrategy] = MissingValueStrategy.DROP_ROW,
        columns: Optional[List[str]] = None,
        fill_value: Any = None,
        threshold: float = 0.5,
    ) -> ProcessingResult:
        if isinstance(strategy, str):
            strategy = MissingValueStrategy(strategy)

        before = self._take_snapshot(self.df)
        target_cols = columns if columns else list(self.df.columns)
        target_cols = [c for c in target_cols if c in self.df.columns]

        if not target_cols:
            return self._record(ProcessingResult(
                success=False,
                message="指定的列不存在",
                before_stats=before,
                after_stats=before,
            ))

        rows_before = len(self.df)

        if strategy == MissingValueStrategy.DROP_ROW:
            self.df = self.df.dropna(subset=target_cols)
            rows_affected = rows_before - len(self.df)
            msg = f"删除了 {rows_affected} 行包含缺失值的数据"

        elif strategy == MissingValueStrategy.DROP_COLUMN:
            drop_cols = [
                c for c in target_cols
                if self.df[c].isnull().mean() >= threshold
            ]
            self.df = self.df.drop(columns=drop_cols)
            rows_affected = 0
            msg = f"删除了 {len(drop_cols)} 列缺失率超过 {threshold:.0%} 的列: {drop_cols}"

        elif strategy == MissingValueStrategy.FILL_MEAN:
            numeric_cols = self._get_numeric_columns(target_cols)
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
            rows_affected = sum(before.null_counts[c] for c in numeric_cols)
            msg = f"使用均值填充了 {len(numeric_cols)} 列的缺失值"

        elif strategy == MissingValueStrategy.FILL_MEDIAN:
            numeric_cols = self._get_numeric_columns(target_cols)
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
            rows_affected = sum(before.null_counts[c] for c in numeric_cols)
            msg = f"使用中位数填充了 {len(numeric_cols)} 列的缺失值"

        elif strategy == MissingValueStrategy.FILL_MODE:
            filled = 0
            for col in target_cols:
                mode_val = self.df[col].mode()
                if not mode_val.empty:
                    null_count = self.df[col].isnull().sum()
                    self.df[col] = self.df[col].fillna(mode_val.iloc[0])
                    filled += null_count
            rows_affected = filled
            msg = f"使用众数填充了 {len(target_cols)} 列的缺失值"

        elif strategy == MissingValueStrategy.FILL_VALUE:
            if fill_value is None:
                return self._record(ProcessingResult(
                    success=False,
                    message="使用固定值填充时必须提供 fill_value 参数",
                    before_stats=before,
                    after_stats=before,
                ))
            null_total = sum(self.df[c].isnull().sum() for c in target_cols)
            self.df[target_cols] = self.df[target_cols].fillna(fill_value)
            rows_affected = null_total
            msg = f"使用固定值 '{fill_value}' 填充了缺失值"

        elif strategy == MissingValueStrategy.FILL_FFILL:
            null_total = sum(self.df[c].isnull().sum() for c in target_cols)
            self.df[target_cols] = self.df[target_cols].ffill()
            new_null = sum(self.df[c].isnull().sum() for c in target_cols)
            rows_affected = null_total - new_null
            msg = f"使用前向填充处理了 {rows_affected} 个缺失值"

        elif strategy == MissingValueStrategy.FILL_BFILL:
            null_total = sum(self.df[c].isnull().sum() for c in target_cols)
            self.df[target_cols] = self.df[target_cols].bfill()
            new_null = sum(self.df[c].isnull().sum() for c in target_cols)
            rows_affected = null_total - new_null
            msg = f"使用后向填充处理了 {rows_affected} 个缺失值"

        elif strategy == MissingValueStrategy.MARK:
            for col in target_cols:
                mark_col = f"{col}_is_missing"
                self.df[mark_col] = self.df[col].isnull().astype(int)
            rows_affected = 0
            msg = f"为 {len(target_cols)} 列添加了缺失值标记列"

        else:
            return self._record(ProcessingResult(
                success=False,
                message=f"不支持的策略: {strategy}",
                before_stats=before,
                after_stats=before,
            ))

        after = self._take_snapshot(self.df)
        return self._record(ProcessingResult(
            success=True,
            message=msg,
            rows_affected=rows_affected,
            columns_affected=len(target_cols) if strategy == MissingValueStrategy.MARK else 0,
            before_stats=before,
            after_stats=after,
            details={"strategy": strategy.value, "columns": target_cols},
        ))

    def remove_duplicates(
        self,
        subset: Optional[List[str]] = None,
        keep: Literal["first", "last", False] = "first",
    ) -> ProcessingResult:
        before = self._take_snapshot(self.df)
        rows_before = len(self.df)

        if subset:
            valid_cols = [c for c in subset if c in self.df.columns]
            if not valid_cols:
                return self._record(ProcessingResult(
                    success=False,
                    message="指定的列不存在",
                    before_stats=before,
                    after_stats=before,
                ))
            subset = valid_cols

        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        rows_removed = rows_before - len(self.df)
        after = self._take_snapshot(self.df)

        return self._record(ProcessingResult(
            success=True,
            message=f"删除了 {rows_removed} 行重复数据",
            rows_affected=rows_removed,
            before_stats=before,
            after_stats=after,
            details={"subset": subset, "keep": keep},
        ))

    def detect_outliers(
        self,
        columns: Optional[List[str]] = None,
        method: Union[str, OutlierMethod] = OutlierMethod.IQR,
        threshold: float = 1.5,
        zscore_threshold: float = 3.0,
    ) -> Dict[str, List[int]]:
        if isinstance(method, str):
            method = OutlierMethod(method)

        numeric_cols = self._get_numeric_columns(columns)
        if not numeric_cols:
            return {}

        outlier_indices: Dict[str, List[int]] = {}

        for col in numeric_cols:
            series = self.df[col].dropna()

            if method == OutlierMethod.IQR:
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                mask = (self.df[col] < lower) | (self.df[col] > upper)
            else:
                mean = series.mean()
                std = series.std()
                if std == 0:
                    continue
                z_scores = np.abs((self.df[col] - mean) / std)
                mask = z_scores > zscore_threshold

            indices = self.df.index[mask].tolist()
            if indices:
                outlier_indices[col] = indices

        return outlier_indices

    def handle_outliers(
        self,
        columns: Optional[List[str]] = None,
        method: Union[str, OutlierMethod] = OutlierMethod.IQR,
        action: Union[str, OutlierAction] = OutlierAction.CAP,
        threshold: float = 1.5,
        zscore_threshold: float = 3.0,
    ) -> ProcessingResult:
        if isinstance(method, str):
            method = OutlierMethod(method)
        if isinstance(action, str):
            action = OutlierAction(action)

        before = self._take_snapshot(self.df)
        outlier_map = self.detect_outliers(columns, method, threshold, zscore_threshold)

        if not outlier_map:
            return self._record(ProcessingResult(
                success=True,
                message="未检测到异常值",
                before_stats=before,
                after_stats=before,
            ))

        total_outliers = sum(len(v) for v in outlier_map.values())
        affected_cols = list(outlier_map.keys())

        if action == OutlierAction.REMOVE:
            all_indices: Set[int] = set()
            for indices in outlier_map.values():
                all_indices.update(indices)
            self.df = self.df.drop(index=list(all_indices))
            msg = f"删除了 {len(all_indices)} 行异常值数据"

        elif action == OutlierAction.CAP:
            for col in affected_cols:
                series = self.df[col].dropna()
                if method == OutlierMethod.IQR:
                    q1, q3 = series.quantile(0.25), series.quantile(0.75)
                    iqr = q3 - q1
                    lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
                else:
                    mean, std = series.mean(), series.std()
                    lower = mean - zscore_threshold * std
                    upper = mean + zscore_threshold * std
                self.df[col] = self.df[col].clip(lower=lower, upper=upper)
            msg = f"将 {len(affected_cols)} 列的异常值截断到边界值"

        elif action == OutlierAction.MARK:
            for col in affected_cols:
                mark_col = f"{col}_is_outlier"
                self.df[mark_col] = 0
                self.df.loc[outlier_map[col], mark_col] = 1
            msg = f"为 {len(affected_cols)} 列添加了异常值标记列"

        elif action in (OutlierAction.MEDIAN, OutlierAction.MEAN):
            agg_func = "median" if action == OutlierAction.MEDIAN else "mean"
            for col in affected_cols:
                agg_val = getattr(self.df[col].dropna(), agg_func)()
                self.df.loc[outlier_map[col], col] = agg_val
            msg = f"将 {len(affected_cols)} 列的异常值替换为{action.value}"

        else:
            return self._record(ProcessingResult(
                success=False,
                message=f"不支持的处理方式: {action}",
                before_stats=before,
                after_stats=before,
            ))

        after = self._take_snapshot(self.df)
        return self._record(ProcessingResult(
            success=True,
            message=msg,
            rows_affected=total_outliers,
            columns_affected=len(affected_cols),
            before_stats=before,
            after_stats=after,
            details={
                "method": method.value,
                "action": action.value,
                "outlier_map": {k: len(v) for k, v in outlier_map.items()},
            },
        ))

    def convert_type(
        self,
        column: str,
        target_type: str,
        date_format: Optional[str] = None,
        errors: Literal["raise", "coerce", "ignore"] = "coerce",
        fill_value: Any = None,
    ) -> ProcessingResult:
        if column not in self.df.columns:
            return self._record(ProcessingResult(
                success=False,
                message=f"列 '{column}' 不存在",
            ))

        before = self._take_snapshot(self.df)
        original_dtype = str(self.df[column].dtype)

        try:
            if target_type in ("int", "int64", "int32"):
                converted = pd.to_numeric(self.df[column], errors=errors)
                if fill_value is not None:
                    converted = converted.fillna(fill_value)
                self.df[column] = converted.astype("Int64")

            elif target_type in ("float", "float64", "float32"):
                converted = pd.to_numeric(self.df[column], errors=errors)
                if fill_value is not None:
                    converted = converted.fillna(fill_value)
                self.df[column] = converted

            elif target_type in ("str", "string"):
                self.df[column] = self.df[column].astype(str).replace("nan", np.nan)

            elif target_type in ("datetime", "date"):
                self.df[column] = pd.to_datetime(
                    self.df[column], format=date_format, errors=errors
                )
                if target_type == "date":
                    self.df[column] = self.df[column].dt.date

            elif target_type in ("bool", "boolean"):
                bool_map = {
                    "true": True, "false": False,
                    "是": True, "否": False,
                    "1": True, "0": False,
                    "yes": True, "no": False,
                }
                self.df[column] = (
                    self.df[column]
                    .astype(str).str.lower().map(bool_map)
                    .fillna(self.df[column])
                )

            elif target_type == "category":
                self.df[column] = self.df[column].astype("category")

            else:
                return self._record(ProcessingResult(
                    success=False,
                    message=f"不支持的目标类型: {target_type}",
                    before_stats=before,
                    after_stats=before,
                ))

        except Exception as e:
            return self._record(ProcessingResult(
                success=False,
                message=f"类型转换失败: {e}",
                before_stats=before,
                after_stats=before,
            ))

        after = self._take_snapshot(self.df)
        new_dtype = str(self.df[column].dtype)
        return self._record(ProcessingResult(
            success=True,
            message=f"列 '{column}' 类型从 {original_dtype} 转换为 {new_dtype}",
            columns_affected=1,
            before_stats=before,
            after_stats=after,
            details={"column": column, "from": original_dtype, "to": new_dtype},
        ))

    def rename_columns(self, mapping: Dict[str, str]) -> ProcessingResult:
        invalid = [k for k in mapping if k not in self.df.columns]
        if invalid:
            return self._record(ProcessingResult(
                success=False,
                message=f"以下列不存在: {invalid}",
            ))

        before = self._take_snapshot(self.df)
        self.df = self.df.rename(columns=mapping)
        after = self._take_snapshot(self.df)

        return self._record(ProcessingResult(
            success=True,
            message=f"重命名了 {len(mapping)} 列",
            columns_affected=len(mapping),
            before_stats=before,
            after_stats=after,
            details={"mapping": mapping},
        ))

    def normalize(
        self,
        columns: Optional[List[str]] = None,
        method: Union[str, NormalizeMethod] = NormalizeMethod.MINMAX,
        feature_range: Tuple[float, float] = (0.0, 1.0),
    ) -> ProcessingResult:
        if isinstance(method, str):
            method = NormalizeMethod(method)

        before = self._take_snapshot(self.df)
        numeric_cols = self._get_numeric_columns(columns)

        if not numeric_cols:
            return self._record(ProcessingResult(
                success=False,
                message="没有可标准化的数值列",
                before_stats=before,
                after_stats=before,
            ))

        params: Dict[str, Any] = {}

        for col in numeric_cols:
            series = self.df[col].astype(float)

            if method == NormalizeMethod.MINMAX:
                min_val = series.min()
                max_val = series.max()
                span = max_val - min_val
                if span == 0:
                    self.df[col] = feature_range[0]
                else:
                    scaled = (series - min_val) / span
                    self.df[col] = scaled * (feature_range[1] - feature_range[0]) + feature_range[0]
                params[col] = {"min": float(min_val), "max": float(max_val)}

            elif method == NormalizeMethod.ZSCORE:
                mean_val = series.mean()
                std_val = series.std()
                if std_val == 0:
                    self.df[col] = 0.0
                else:
                    self.df[col] = (series - mean_val) / std_val
                params[col] = {"mean": float(mean_val), "std": float(std_val)}

            elif method == NormalizeMethod.MAXABS:
                max_abs = series.abs().max()
                if max_abs == 0:
                    self.df[col] = 0.0
                else:
                    self.df[col] = series / max_abs
                params[col] = {"max_abs": float(max_abs)}

        after = self._take_snapshot(self.df)
        return self._record(ProcessingResult(
            success=True,
            message=f"使用 {method.value} 方法标准化了 {len(numeric_cols)} 列",
            columns_affected=len(numeric_cols),
            before_stats=before,
            after_stats=after,
            details={"method": method.value, "columns": numeric_cols, "params": params},
        ))

    def validate(
        self,
        rules: List[ValidationRule],
        sample_size: Optional[int] = None,
    ) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []
        details: Dict[str, Any] = {"rule_results": []}

        df = self.df.sample(n=min(sample_size, len(self.df))) if sample_size and len(self.df) > sample_size else self.df

        for rule in rules:
            if rule.column not in self.df.columns:
                err = rule.error_message or f"列 '{rule.column}' 不存在"
                errors.append(err)
                details["rule_results"].append({
                    "column": rule.column, "rule": rule.rule_type, "passed": False, "message": err,
                })
                continue

            series = df[rule.column]
            result = self._check_rule(series, rule)

            entry = {
                "column": rule.column,
                "rule": rule.rule_type,
                "passed": result[0],
                "message": result[1],
            }
            details["rule_results"].append(entry)

            if result[0]:
                passed.append(f"{rule.column}: {rule.rule_type} - 通过")
            else:
                msg = rule.error_message or result[1]
                if result[2]:
                    warnings.append(msg)
                else:
                    errors.append(msg)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checks_passed=passed,
            details=details,
        )

    def _check_rule(self, series: pd.Series, rule: ValidationRule) -> Tuple[bool, str, bool]:
        rtype = rule.rule_type
        params = rule.params

        if rtype == "not_null":
            null_count = series.isnull().sum()
            if null_count > 0:
                return (False, f"列 '{rule.column}' 存在 {null_count} 个空值", False)
            return (True, "无空值", False)

        if rtype == "unique":
            dup_count = series.duplicated().sum()
            if dup_count > 0:
                return (False, f"列 '{rule.column}' 存在 {dup_count} 个重复值", False)
            return (True, "值唯一", False)

        if rtype == "range":
            min_val = params.get("min")
            max_val = params.get("max")
            numeric = pd.to_numeric(series, errors="coerce")
            if min_val is not None:
                below = (numeric < min_val).sum()
                if below > 0:
                    return (False, f"列 '{rule.column}' 有 {below} 个值低于最小值 {min_val}", False)
            if max_val is not None:
                above = (numeric > max_val).sum()
                if above > 0:
                    return (False, f"列 '{rule.column}' 有 {above} 个值超过最大值 {max_val}", False)
            return (True, f"值在 [{min_val}, {max_val}] 范围内", False)

        if rtype == "min_length":
            min_len = params.get("min", 0)
            short = series.dropna().astype(str).str.len() < min_len
            count = short.sum()
            if count > 0:
                return (False, f"列 '{rule.column}' 有 {count} 个值长度不足 {min_len}", False)
            return (True, f"最小长度 >= {min_len}", False)

        if rtype == "max_length":
            max_len = params.get("max", float("inf"))
            long = series.dropna().astype(str).str.len() > max_len
            count = long.sum()
            if count > 0:
                return (False, f"列 '{rule.column}' 有 {count} 个值长度超过 {max_len}", False)
            return (True, f"最大长度 <= {max_len}", False)

        if rtype == "regex":
            import re
            pattern = params.get("pattern", "")
            if not pattern:
                return (True, "无正则表达式", True)
            non_null = series.dropna().astype(str)
            match = non_null.str.match(pattern)
            mismatch = (~match).sum()
            if mismatch > 0:
                return (False, f"列 '{rule.column}' 有 {mismatch} 个值不匹配正则 '{pattern}'", False)
            return (True, f"匹配正则 '{pattern}'", False)

        if rtype == "allowed_values":
            allowed = set(params.get("values", []))
            if not allowed:
                return (True, "无允许值列表", True)
            non_null = series.dropna()
            invalid = set(non_null.unique()) - allowed
            if invalid:
                preview = list(invalid)[:5]
                return (False, f"列 '{rule.column}' 存在不允许的值: {preview}", False)
            return (True, f"值在允许列表中", False)

        if rtype == "dtype":
            expected = params.get("dtype", "")
            actual = str(series.dtype)
            if expected and not actual.startswith(expected):
                return (False, f"列 '{rule.column}' 类型为 {actual}，期望 {expected}", False)
            return (True, f"类型为 {actual}", False)

        if rtype == "max_null_ratio":
            max_ratio = params.get("ratio", 1.0)
            actual_ratio = series.isnull().mean()
            if actual_ratio > max_ratio:
                return (False, f"列 '{rule.column}' 缺失率 {actual_ratio:.1%} 超过 {max_ratio:.1%}", True)
            return (True, f"缺失率 {actual_ratio:.1%} 在允许范围内", False)

        return (False, f"未知规则类型: {rtype}", True)

    def validate_schema(
        self,
        required_columns: Optional[List[str]] = None,
        column_types: Optional[Dict[str, str]] = None,
        max_null_ratio: float = 0.5,
        forbid_duplicates: bool = False,
    ) -> ValidationResult:
        rules: List[ValidationRule] = []

        if required_columns:
            for col in required_columns:
                if col not in self.df.columns:
                    rules.append(ValidationRule(
                        column=col, rule_type="not_null",
                        error_message=f"缺少必需列: {col}",
                    ))

        if column_types:
            for col, dtype in column_types.items():
                rules.append(ValidationRule(column=col, rule_type="dtype", params={"dtype": dtype}))

        for col in self.df.columns:
            rules.append(ValidationRule(
                column=col, rule_type="max_null_ratio",
                params={"ratio": max_null_ratio},
            ))

        if forbid_duplicates:
            if required_columns:
                for col in required_columns:
                    if col in self.df.columns:
                        rules.append(ValidationRule(column=col, rule_type="unique"))

        return self.validate(rules)

    def get_change_log(self) -> List[Dict[str, Any]]:
        log = []
        for i, result in enumerate(self._history, 1):
            entry: Dict[str, Any] = {
                "step": i,
                "success": result.success,
                "message": result.message,
                "rows_affected": result.rows_affected,
                "columns_affected": result.columns_affected,
            }
            if result.details:
                entry["details"] = result.details
            log.append(entry)
        return log

    def export_processed(self) -> pd.DataFrame:
        return self.df.copy()

    def quick_clean(
        self,
        fill_strategy: Union[str, MissingValueStrategy] = MissingValueStrategy.FILL_MEDIAN,
        remove_dup: bool = True,
        handle_outliers_flag: bool = True,
        outlier_method: Union[str, OutlierMethod] = OutlierMethod.IQR,
    ) -> List[ProcessingResult]:
        results = []

        result = self.handle_missing_values(strategy=fill_strategy)
        results.append(result)

        if remove_dup:
            result = self.remove_duplicates()
            results.append(result)

        if handle_outliers_flag:
            result = self.handle_outliers(method=outlier_method, action=OutlierAction.CAP)
            results.append(result)

        return results
