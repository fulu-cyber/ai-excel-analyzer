import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    non_null_count: int
    null_count: int
    null_ratio: float
    unique_count: Optional[int] = None
    stats: Optional[Dict[str, Any]] = None


@dataclass
class DataProfile:
    row_count: int
    column_count: int
    columns: List[ColumnProfile] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DataProfiler:
    NUMERIC_TYPES = {'int16', 'int32', 'int64', 'float16', 'float32', 'float64', 'uint8', 'uint16', 'uint32', 'uint64'}
    CATEGORICAL_THRESHOLD = 0.05

    def __init__(self, df: pd.DataFrame):
        self._validate_input(df)
        self.df = df
        self.profile: Optional[DataProfile] = None

    def _validate_input(self, df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"输入必须是pandas DataFrame，收到: {type(df).__name__}")

    def _is_numeric(self, series: pd.Series) -> bool:
        return series.dtype.name in self.NUMERIC_TYPES

    def _is_categorical(self, series: pd.Series) -> bool:
        if series.dtype.name == 'object' or series.dtype.name == 'category':
            return True
        if self._is_numeric(series):
            unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
            return unique_ratio < self.CATEGORICAL_THRESHOLD
        return False

    def _get_dtype_display(self, series: pd.Series) -> str:
        dtype_map = {
            'int64': '整数',
            'int32': '整数',
            'int16': '整数',
            'float64': '浮点数',
            'float32': '浮点数',
            'object': '文本',
            'category': '分类',
            'bool': '布尔',
            'datetime64[ns]': '日期时间',
        }
        return dtype_map.get(series.dtype.name, series.dtype.name)

    def _profile_numeric_column(self, series: pd.Series) -> Dict[str, Any]:
        clean_series = series.dropna()
        if len(clean_series) == 0:
            return {
                'mean': None,
                'median': None,
                'std': None,
                'min': None,
                'max': None,
                'q25': None,
                'q75': None,
            }

        return {
            'mean': round(float(clean_series.mean()), 4),
            'median': round(float(clean_series.median()), 4),
            'std': round(float(clean_series.std()), 4),
            'min': float(clean_series.min()),
            'max': float(clean_series.max()),
            'q25': round(float(clean_series.quantile(0.25)), 4),
            'q75': round(float(clean_series.quantile(0.75)), 4),
        }

    def _profile_categorical_column(self, series: pd.Series) -> Dict[str, Any]:
        clean_series = series.dropna()
        if len(clean_series) == 0:
            return {
                'unique_count': 0,
                'top_values': [],
            }

        value_counts = clean_series.value_counts()
        top_values = [
            {'value': str(val), 'count': int(count), 'ratio': round(count / len(clean_series), 4)}
            for val, count in value_counts.head(5).items()
        ]

        return {
            'unique_count': int(clean_series.nunique()),
            'top_values': top_values,
        }

    def _detect_warnings(self) -> List[str]:
        warnings = []

        if len(self.df) == 0:
            warnings.append("数据为空DataFrame，不包含任何行")

        if len(self.df.columns) == 0:
            warnings.append("数据不包含任何列")

        for col in self.df.columns:
            null_ratio = self.df[col].isnull().sum() / len(self.df) if len(self.df) > 0 else 0
            if null_ratio == 1.0:
                warnings.append(f"列 '{col}' 全部为缺失值")
            elif null_ratio > 0.5:
                warnings.append(f"列 '{col}' 缺失值比例超过50% ({null_ratio:.1%})")

        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            warnings.append(f"存在 {duplicate_count} 行重复数据")

        return warnings

    def profile_column(self, series: pd.Series) -> ColumnProfile:
        non_null_count = int(series.notnull().sum())
        null_count = int(series.isnull().sum())
        null_ratio = round(null_count / len(series), 4) if len(series) > 0 else 0.0

        is_numeric = self._is_numeric(series)
        is_categorical = self._is_categorical(series)

        stats = None
        unique_count = None

        if is_numeric:
            stats = self._profile_numeric_column(series)
        if is_categorical:
            cat_stats = self._profile_categorical_column(series)
            unique_count = cat_stats['unique_count']
            if stats is None:
                stats = cat_stats
            else:
                stats.update(cat_stats)

        return ColumnProfile(
            name=series.name,
            dtype=self._get_dtype_display(series),
            non_null_count=non_null_count,
            null_count=null_count,
            null_ratio=null_ratio,
            unique_count=unique_count,
            stats=stats,
        )

    def generate_profile(self) -> DataProfile:
        warnings = self._detect_warnings()
        columns = [self.profile_column(self.df[col]) for col in self.df.columns]

        self.profile = DataProfile(
            row_count=len(self.df),
            column_count=len(self.df.columns),
            columns=columns,
            warnings=warnings,
        )
        return self.profile

    def _format_column_report(self, col: ColumnProfile) -> str:
        lines = []
        lines.append(f"  列名: {col.name}")
        lines.append(f"    类型: {col.dtype}")
        lines.append(f"    非空值: {col.non_null_count} | 缺失值: {col.null_count} ({col.null_ratio:.1%})")

        if col.stats is not None:
            if 'mean' in col.stats and col.stats['mean'] is not None:
                lines.append(f"    均值: {col.stats['mean']}")
                lines.append(f"    中位数: {col.stats['median']}")
                lines.append(f"    标准差: {col.stats['std']}")
                lines.append(f"    最小值: {col.stats['min']} | 最大值: {col.stats['max']}")
                lines.append(f"    25%分位: {col.stats['q25']} | 75%分位: {col.stats['q75']}")

            if 'unique_count' in col.stats:
                lines.append(f"    唯一值数量: {col.stats['unique_count']}")

            if 'top_values' in col.stats and col.stats['top_values']:
                lines.append("    最常见的值:")
                for item in col.stats['top_values'][:3]:
                    lines.append(f"      - {item['value']}: {item['count']}次 ({item['ratio']:.1%})")

        return '\n'.join(lines)

    def format_report(self, profile: Optional[DataProfile] = None) -> str:
        if profile is None:
            if self.profile is None:
                profile = self.generate_profile()
            else:
                profile = self.profile

        lines = []
        lines.append("=" * 60)
        lines.append("数据画像报告")
        lines.append("=" * 60)
        lines.append("")

        lines.append(f"数据维度: {profile.row_count} 行 × {profile.column_count} 列")
        lines.append("")

        if profile.warnings:
            lines.append("-" * 40)
            lines.append("[!] 警告信息:")
            for warning in profile.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        lines.append("-" * 40)
        lines.append("列详情:")
        lines.append("-" * 40)
        for col in profile.columns:
            lines.append(self._format_column_report(col))
            lines.append("")

        lines.append("=" * 60)
        return '\n'.join(lines)

    def get_summary(self) -> Dict[str, Any]:
        if self.profile is None:
            self.generate_profile()

        numeric_cols = [col.name for col in self.profile.columns if self._is_numeric(self.df[col.name])]
        categorical_cols = [col.name for col in self.profile.columns if self._is_categorical(self.df[col.name])]
        total_null = sum(col.null_count for col in self.profile.columns)
        total_cells = self.profile.row_count * self.profile.column_count

        return {
            'row_count': self.profile.row_count,
            'column_count': self.profile.column_count,
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'total_null_count': total_null,
            'total_null_ratio': round(total_null / total_cells, 4) if total_cells > 0 else 0.0,
            'warnings': self.profile.warnings,
        }
