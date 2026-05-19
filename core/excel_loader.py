import pandas as pd
from pathlib import Path
from typing import Optional, List, Union, Iterator, Dict
import os

from config import Config


class ExcelLoader:
    SUPPORTED_EXTENSIONS = {'.xlsx', '.xls'}

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self._validate_file()
        self._sheet_names: Optional[List[str]] = None

    def _validate_file(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        if not self.file_path.is_file():
            raise ValueError(f"路径不是文件: {self.file_path}")

        suffix = self.file_path.suffix.lower()
        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {suffix}，支持的格式: {self.SUPPORTED_EXTENSIONS}")

        file_size_mb = self.file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > Config.MAX_FILE_SIZE_MB:
            raise ValueError(f"文件大小超过限制: {file_size_mb:.2f}MB > {Config.MAX_FILE_SIZE_MB}MB")

    def get_sheet_names(self) -> List[str]:
        if self._sheet_names is not None:
            return self._sheet_names

        try:
            engine = self._get_engine()
            if engine == 'openpyxl':
                import openpyxl
                wb = openpyxl.load_workbook(self.file_path, read_only=True)
                self._sheet_names = wb.sheetnames
                wb.close()
            elif engine == 'xlrd':
                import xlrd
                wb = xlrd.open_workbook(str(self.file_path))
                self._sheet_names = wb.sheet_names()
            return self._sheet_names
        except Exception as e:
            raise RuntimeError(f"读取工作表名称失败: {e}")

    def _get_engine(self) -> str:
        suffix = self.file_path.suffix.lower()
        if suffix == '.xlsx':
            return 'openpyxl'
        elif suffix == '.xls':
            return 'xlrd'
        raise ValueError(f"无法确定读取引擎: {suffix}")

    def load(
        self,
        sheet_name: Optional[Union[str, int]] = 0,
        header: Optional[int] = 0,
        nrows: Optional[int] = None,
        usecols: Optional[Union[str, List]] = None
    ) -> pd.DataFrame:
        try:
            engine = self._get_engine()
            df = pd.read_excel(
                self.file_path,
                sheet_name=sheet_name,
                engine=engine,
                header=header,
                nrows=nrows,
                usecols=usecols
            )
            return df
        except Exception as e:
            raise RuntimeError(f"读取Excel文件失败: {e}")

    def load_chunked(
        self,
        sheet_name: Optional[Union[str, int]] = 0,
        chunk_size: Optional[int] = None,
        header: Optional[int] = 0,
        usecols: Optional[Union[str, List]] = None
    ) -> Iterator[pd.DataFrame]:
        if chunk_size is None:
            chunk_size = Config.CHUNK_SIZE

        try:
            engine = self._get_engine()
            df_full = pd.read_excel(
                self.file_path,
                sheet_name=sheet_name,
                engine=engine,
                header=header,
                usecols=usecols
            )

            total_rows = len(df_full)
            for start in range(0, total_rows, chunk_size):
                end = min(start + chunk_size, total_rows)
                yield df_full.iloc[start:end].copy()

        except Exception as e:
            raise RuntimeError(f"分块读取Excel文件失败: {e}")

    def load_all_sheets(self) -> Dict[str, pd.DataFrame]:
        sheet_names = self.get_sheet_names()
        result = {}
        for name in sheet_names:
            result[name] = self.load(sheet_name=name)
        return result