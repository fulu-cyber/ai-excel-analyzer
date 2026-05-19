from datetime import datetime
from typing import Any, Dict, List, Optional

from jinja2 import Environment, BaseLoader, TemplateError

from .data_profiler import DataProfile, ColumnProfile


REPORT_TEMPLATE = """# {{ title }}

> 生成时间：{{ generated_at }}

---

## 一、数据概览

### 基本信息

| 指标 | 值 |
|------|-----|
| 数据行数 | {{ profile.row_count | format_number }} |
| 数据列数 | {{ profile.column_count }} |
| 总单元格数 | {{ (profile.row_count * profile.column_count) | format_number }} |
| 数据质量评分 | {{ quality_score }}/100 |

{% if profile.warnings %}
### 质量警告

{% for warning in profile.warnings %}
- :warning: {{ warning }}
{% endfor %}
{% endif %}

### 列信息详情

| 列名 | 数据类型 | 非空值 | 缺失值 | 缺失率 |
|------|----------|--------|--------|--------|
{% for col in profile.columns %}
| {{ col.name }} | {{ col.dtype }} | {{ col.non_null_count | format_number }} | {{ col.null_count | format_number }} | {{ "%.1f" | format(col.null_ratio * 100) }}% |
{% endfor %}

{% if numeric_summary %}
### 数值列统计

| 列名 | 均值 | 中位数 | 标准差 | 最小值 | 最大值 |
|------|------|--------|--------|--------|--------|
{% for item in numeric_summary %}
| {{ item.name }} | {{ "%.2f" | format(item.mean) }} | {{ "%.2f" | format(item.median) }} | {{ "%.2f" | format(item.std) }} | {{ "%.2f" | format(item.min) }} | {{ "%.2f" | format(item.max) }} |
{% endfor %}
{% endif %}

---

## 二、关键发现

{% if key_findings %}
{% for finding in key_findings %}
{{ loop.index }}. **{{ finding.title }}**
   {{ finding.description }}
{% endfor %}
{% else %}
暂无关键发现。
{% endif %}

---

## 三、AI 分析洞察

{% if ai_insights %}
{{ ai_insights }}
{% else %}
暂无AI分析洞察。
{% endif %}

---

## 四、建议和下一步行动

{% if recommendations %}
{% for rec in recommendations %}
### {{ rec.category }}

{% for action in rec.actions %}
- {{ action }}
{% endfor %}
{% endfor %}
{% else %}
暂无建议。
{% endif %}

---

{% if footer %}
{{ footer }}
{% endif %}

*本报告由 AI Excel Analyzer 自动生成*
"""


class ReportGeneratorError(Exception):
    pass


class ReportGenerator:

    def __init__(self):
        self._env = Environment(
            loader=BaseLoader(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._env.filters['format_number'] = self._format_number
        self._template = self._env.from_string(REPORT_TEMPLATE)

    @staticmethod
    def _format_number(value: int) -> str:
        if value >= 10000:
            return f"{value / 10000:.1f}万"
        return f"{value:,}"

    @staticmethod
    def _calculate_quality_score(profile: DataProfile) -> int:
        if profile.row_count == 0 or profile.column_count == 0:
            return 0

        score = 100

        total_cells = profile.row_count * profile.column_count
        total_null = sum(col.null_count for col in profile.columns)
        null_ratio = total_null / total_cells if total_cells > 0 else 0
        score -= int(null_ratio * 50)

        warning_count = len(profile.warnings)
        score -= warning_count * 5

        return max(0, min(100, score))

    @staticmethod
    def _extract_numeric_summary(profile: DataProfile) -> List[Dict[str, Any]]:
        summary = []
        for col in profile.columns:
            if col.stats and 'mean' in col.stats and col.stats['mean'] is not None:
                summary.append({
                    'name': col.name,
                    'mean': col.stats['mean'],
                    'median': col.stats['median'],
                    'std': col.stats['std'],
                    'min': col.stats['min'],
                    'max': col.stats['max'],
                })
        return summary

    @staticmethod
    def _generate_key_findings(profile: DataProfile) -> List[Dict[str, str]]:
        findings = []

        if profile.row_count > 0 and profile.column_count > 0:
            findings.append({
                'title': '数据规模',
                'description': f'数据集包含 {profile.row_count:,} 行 × {profile.column_count} 列，共 {profile.row_count * profile.column_count:,} 个数据单元。',
            })

        high_null_cols = [
            col for col in profile.columns
            if col.null_ratio > 0.1
        ]
        if high_null_cols:
            col_names = '、'.join([col.name for col in high_null_cols[:3]])
            findings.append({
                'title': '数据完整性',
                'description': f'存在 {len(high_null_cols)} 列缺失值超过10%，包括：{col_names}。建议进行数据清洗。',
            })

        numeric_cols = [
            col for col in profile.columns
            if col.stats and 'mean' in col.stats and col.stats['mean'] is not None
        ]
        if numeric_cols:
            findings.append({
                'title': '数值特征',
                'description': f'发现 {len(numeric_cols)} 个数值型列，可用于统计分析和建模。',
            })

        categorical_cols = [
            col for col in profile.columns
            if col.stats and 'unique_count' in col.stats
        ]
        if categorical_cols:
            findings.append({
                'title': '分类特征',
                'description': f'发现 {len(categorical_cols)} 个分类型列，可用于分组分析。',
            })

        if profile.warnings:
            findings.append({
                'title': '质量警告',
                'description': f'检测到 {len(profile.warnings)} 个数据质量问题，需要关注。',
            })

        return findings

    @staticmethod
    def _generate_recommendations(
        profile: DataProfile,
        ai_insights: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        recommendations = []

        data_actions = []
        high_null_cols = [col for col in profile.columns if col.null_ratio > 0.2]
        if high_null_cols:
            data_actions.append('处理高缺失率列：考虑删除或填充缺失值')
        if any('重复' in w for w in profile.warnings):
            data_actions.append('清理重复数据：删除完全重复的行')
        if data_actions:
            recommendations.append({
                'category': '数据清洗',
                'actions': data_actions,
            })

        analysis_actions = []
        numeric_cols = [
            col for col in profile.columns
            if col.stats and 'mean' in col.stats
        ]
        if numeric_cols:
            analysis_actions.append('进行数值分布分析和异常值检测')
        categorical_cols = [
            col for col in profile.columns
            if col.stats and 'unique_count' in col.stats
        ]
        if categorical_cols:
            analysis_actions.append('分析分类变量的分布和占比')
        if len(numeric_cols) >= 2:
            analysis_actions.append('计算数值变量间的相关性')
        if analysis_actions:
            recommendations.append({
                'category': '深入分析',
                'actions': analysis_actions,
            })

        next_actions = ['验证分析结论的业务含义', '根据洞察制定行动计划']
        if not ai_insights:
            next_actions.append('使用AI分析功能获取更深入的洞察')
        recommendations.append({
            'category': '后续步骤',
            'actions': next_actions,
        })

        return recommendations

    def generate(
        self,
        profile: DataProfile,
        ai_insights: Optional[str] = None,
        title: Optional[str] = None,
        footer: Optional[str] = None,
    ) -> str:
        if not isinstance(profile, DataProfile):
            raise ReportGeneratorError(
                f"profile参数必须是DataProfile类型，收到: {type(profile).__name__}"
            )

        quality_score = self._calculate_quality_score(profile)
        numeric_summary = self._extract_numeric_summary(profile)
        key_findings = self._generate_key_findings(profile)
        recommendations = self._generate_recommendations(profile, ai_insights)

        context = {
            'title': title or 'Excel数据分析报告',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'profile': profile,
            'quality_score': quality_score,
            'numeric_summary': numeric_summary,
            'key_findings': key_findings,
            'ai_insights': ai_insights,
            'recommendations': recommendations,
            'footer': footer,
        }

        try:
            return self._template.render(**context)
        except TemplateError as e:
            raise ReportGeneratorError(f"报告生成失败: {e}")

    def generate_preview(
        self,
        profile: DataProfile,
        ai_insights: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        return self.generate(
            profile=profile,
            ai_insights=ai_insights,
            title=title,
        )

    def generate_download(
        self,
        profile: DataProfile,
        ai_insights: Optional[str] = None,
        title: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> tuple[str, str]:
        content = self.generate(
            profile=profile,
            ai_insights=ai_insights,
            title=title,
        )

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"数据分析报告_{timestamp}.md"

        if not filename.endswith('.md'):
            filename += '.md'

        return content, filename
