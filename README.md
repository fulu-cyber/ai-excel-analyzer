# AI Excel Analyzer 📊

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **AI 驱动的 Excel 数据分析工具** - 上传 Excel 文件，AI 自动生成数据概览、智能分析洞察和专业报告

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [效果展示](#效果展示)
- [快速开始](#快速开始)
- [安装步骤](#安装步骤)
- [使用说明](#使用说明)
- [技术架构](#技术架构)
- [开发指南](#开发指南)
- [常见问题 FAQ](#常见问题-faq)
- [许可证](#许可证)

---

## 项目简介

AI Excel Analyzer 是一款基于大语言模型（DeepSeek）的智能 Excel 数据分析工具。它能够自动读取 Excel 文件，生成数据画像，通过 AI 进行深度分析，并输出专业的分析报告。

### 解决的问题

- 📊 **数据分析门槛高**：传统数据分析需要掌握 Python/Excel 高级技能
- ⏱️ **分析效率低**：手动分析数据耗时耗力
- 📝 **报告撰写困难**：从数据到专业报告需要大量时间
- 🔍 **洞察发现难**：难以从海量数据中发现关键趋势和异常

### 适用场景

- 业务人员快速分析销售、财务等数据
- 数据分析师进行初步数据探索
- 产品经理了解用户行为数据
- 学生和研究人员处理实验数据

---

## 功能特性

### 核心功能

| 功能 | 描述 | 状态 |
|------|------|------|
| 📁 Excel 文件读取 | 支持 .xlsx/.xls 格式，自动识别 Sheet | ✅ |
| 📊 AI 数据概览 | 上传后自动生成数据摘要和结构分析 | ✅ |
| 🔍 智能分析洞察 | 深入分析趋势、模式、异常值 | ✅ |
| 💬 自然语言查询 | 用自然语言提问，AI 结合数据回答 | ✅ |
| 📄 可视化报告 | 一键生成 Markdown 格式分析报告 | ✅ |
| 📈 数据画像 | 自动生成列统计、缺失值分析等 | ✅ |

### 技术亮点

- **智能数据画像**：自动识别数据类型、计算统计指标、检测数据质量
- **Prompt Engineering**：精心设计的提示词模板，确保 AI 输出高质量分析
- **流式响应**：支持 AI 流式输出，实时展示分析结果
- **错误处理**：完善的异常处理机制，支持重试和优雅降级
- **模块化设计**：清晰的代码结构，易于扩展和维护

---

## 效果展示

### 应用界面

```
┌─────────────────────────────────────────────────────────────┐
│  📊 AI Excel Analyzer                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📁 上传 Excel 文件                                  │   │
│  │  [选择文件]                                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │  📊 数据概览      │  │  🔍 AI 分析洞察              │   │
│  │                  │  │                              │   │
│  │  • 1000 行 × 8 列 │  │  • 核心发现                  │   │
│  │  • 数据质量: 95分  │  │  • 趋势分析                  │   │
│  │  • 缺失值: 2%     │  │  • 异常值检测                │   │
│  │                  │  │  • 业务建议                  │   │
│  └──────────────────┘  └──────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  💬 自然语言查询                                      │   │
│  │  [输入你的问题...]                              [发送] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 分析报告示例

```markdown
# 数据分析报告

> 生成时间：2024-01-15 14:30:00

## 一、数据概览

| 指标 | 值 |
|------|-----|
| 数据行数 | 1,000 |
| 数据列数 | 8 |
| 数据质量评分 | 95/100 |

## 二、关键发现

1. **销售高峰出现在 Q4**，12 月销售额是全年月均的 2.3 倍
2. **客户复购率仅为 15%**，存在较大的客户留存提升空间
3. **产品 A 贡献了 40% 的收入**，但利润率最低

## 三、AI 分析洞察

### 趋势与模式分析
- 销售呈现明显的季节性波动，Q4 为旺季
- 周末销售额比工作日高 30%

### 业务建议
- 优化产品组合，调整产品 A 的定价策略
- 加大周末促销力度
- 建立客户忠诚度计划提升复购率
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-excel-analyzer.git
cd ai-excel-analyzer
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

创建 `.env` 文件并添加 DeepSeek API Key：

```bash
# .env
DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 4. 启动应用

```bash
streamlit run main.py
```

应用将在 http://localhost:8501 启动。

---

## 安装步骤

### 系统要求

- Python 3.9 或更高版本
- pip 包管理器
- DeepSeek API Key（[获取地址](https://platform.deepseek.com/)）

### 详细安装流程

#### 1. 环境准备

```bash
# 检查 Python 版本
python --version  # 应 >= 3.9

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 2. 安装项目依赖

```bash
pip install -r requirements.txt
```

依赖说明：
- `pandas>=2.0.0` - 数据处理
- `openpyxl>=3.1.0` - 读写 Excel (.xlsx)
- `xlrd>=2.0.0` - 读取 Excel (.xls)
- `streamlit>=1.28.0` - Web 界面
- `Jinja2>=3.1.0` - 模板引擎
- `requests>=2.31.0` - HTTP 请求
- `python-dotenv>=1.0.0` - 环境变量管理

#### 3. 配置环境变量

创建 `.env` 文件：

```env
# 必需配置
DEEPSEEK_API_KEY=sk-your-api-key-here

# 可选配置（有默认值）
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
MAX_FILE_SIZE_MB=50
API_TIMEOUT=60
API_MAX_RETRIES=3
```

#### 4. 验证安装

```bash
# 运行测试（可选）
pytest tests/

# 启动应用
streamlit run main.py
```

### 部署到 Streamlit Cloud

详见 [DEPLOYMENT.md](DEPLOYMENT.md) 文档。

---

## 使用说明

### 基本使用流程

#### 1. 上传 Excel 文件

- 点击文件上传区域
- 选择 `.xlsx` 或 `.xls` 格式的 Excel 文件
- 文件大小限制：50MB（可通过环境变量调整）

#### 2. 查看数据概览

上传后，系统自动生成：
- 数据规模（行数 × 列数）
- 列信息（名称、类型、缺失值）
- 数据质量评分
- AI 生成的数据摘要

#### 3. 获取 AI 分析洞察

点击"开始分析"按钮，AI 将提供：
- 核心发现（3-5 个要点）
- 趋势与模式分析
- 异常值与风险点
- 关联关系分析
- 业务洞察与建议

#### 4. 自然语言查询

在查询框中输入问题，例如：
- "哪个产品销量最高？"
- "销售额的趋势如何？"
- "哪些客户贡献了 80% 的收入？"

AI 将结合数据回答你的问题。

#### 5. 生成分析报告

点击"生成报告"按钮，系统将生成：
- Markdown 格式的完整分析报告
- 包含数据概览、关键发现、AI 洞察
- 可复制或下载使用

### 高级功能

#### 多 Sheet 支持

如果 Excel 文件包含多个 Sheet，可以在侧边栏选择要分析的 Sheet。

#### 数据筛选

支持对数据进行筛选后再分析：
- 按列筛选
- 按值范围筛选
- 按条件筛选

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面层 (Streamlit)                      │
├─────────────────────────────────────────────────────────────┤
│                         main.py                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       核心业务层 (core/)                      │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│ ExcelLoader │DataProfiler │ AIAnalyzer  │ReportGenerator  │
│  文件读取    │  数据画像    │  AI 分析    │  报告生成       │
└─────────────┴─────────────┴─────────────┴─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      基础设施层                               │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   config    │   .env      │ DeepSeek API│   Jinja2        │
│   配置管理   │  环境变量    │  AI 能力    │   模板引擎       │
└─────────────┴─────────────┴─────────────┴─────────────────┘
```

### 目录结构

```
ai-excel-analyzer/
│
├── main.py                      # Streamlit 主入口
├── config.py                    # 配置文件（API 密钥等）
├── requirements.txt             # Python 依赖
│
├── core/                        # 核心功能模块
│   ├── __init__.py             # 模块导出
│   ├── excel_loader.py         # Excel 文件读取
│   ├── data_profiler.py        # 数据画像生成
│   ├── ai_analyzer.py          # AI 分析核心
│   ├── prompt_templates.py     # Prompt 模板
│   └── report_generator.py     # 报告生成器
│
├── utils/                       # 工具模块
│   ├── __init__.py
│   └── data_processor.py       # 数据处理工具
│
├── .streamlit/                  # Streamlit 配置
│   └── config.toml             # 主题和服务器配置
│
├── .env                         # 环境变量（不提交到 Git）
├── .gitignore                   # Git 忽略文件
├── DEPLOYMENT.md                # 部署指南
└── README.md                    # 项目说明
```

### 核心模块说明

#### ExcelLoader (excel_loader.py)

负责 Excel 文件的读取和验证：
- 支持 .xlsx 和 .xls 格式
- 文件大小验证
- Sheet 名称获取
- 分块读取大文件

#### DataProfiler (data_profiler.py)

生成数据画像：
- 列类型识别（数值、分类、文本、日期）
- 统计指标计算（均值、中位数、标准差等）
- 缺失值分析
- 数据质量评估

#### AIAnalyzer (ai_analyzer.py)

AI 分析核心：
- 调用 DeepSeek API
- 流式响应处理
- 错误重试机制
- 多种分析模式（概览、洞察、查询）

#### PromptTemplates (prompt_templates.py)

精心设计的提示词模板：
- 系统提示词：定义 AI 角色
- 数据概览模板：生成数据摘要
- 分析洞察模板：深度分析
- 查询模板：自然语言问答

#### ReportGenerator (report_generator.py)

报告生成器：
- Jinja2 模板渲染
- Markdown 格式输出
- 数据格式化
- 图表建议

### 技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 编程语言 | Python | 3.9+ | 主要开发语言 |
| Web 框架 | Streamlit | 1.28+ | 用户界面 |
| 数据处理 | pandas | 2.0+ | Excel 读取和数据处理 |
| Excel 读取 | openpyxl/xlrd | 3.1+/2.0+ | .xlsx/.xls 文件支持 |
| AI 能力 | DeepSeek API | - | 大语言模型分析 |
| 模板引擎 | Jinja2 | 3.1+ | 报告模板渲染 |
| HTTP 客户端 | requests | 2.31+ | API 调用 |
| 环境管理 | python-dotenv | 1.0+ | .env 文件加载 |

---

## 开发指南

### 开发环境搭建

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-excel-analyzer.git
cd ai-excel-analyzer
```

#### 2. 创建开发环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install pytest black flake8 mypy
```

#### 3. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，添加你的 API Key
```

### 代码规范

#### 代码风格

- 遵循 PEP 8 规范
- 使用类型注解
- 编写清晰的文档字符串

```python
def analyze_data(df: pd.DataFrame, options: Optional[Dict[str, Any]] = None) -> AnalysisResult:
    """
    分析 DataFrame 数据
    
    Args:
        df: 要分析的 DataFrame
        options: 分析选项
        
    Returns:
        AnalysisResult: 分析结果
    """
    pass
```

#### 命名规范

- 类名：PascalCase（如 `DataProfiler`）
- 函数名：snake_case（如 `analyze_data`）
- 常量：UPPER_SNAKE_CASE（如 `MAX_FILE_SIZE`）
- 私有方法：前缀下划线（如 `_validate_input`）

### 添加新功能

#### 1. 添加新的分析类型

```python
# 1. 在 prompt_templates.py 添加新模板
NEW_ANALYSIS_TEMPLATE = PromptTemplate(
    name="新分析类型",
    role_definition="...",
    task_description="...",
    output_format="...",
    constraints=PromptConstraints(...)
)

# 2. 在 ai_analyzer.py 添加新方法
def analyze_new_type(self, profile: DataProfile, sample_data: str) -> str:
    prompt = get_new_analysis_prompt(profile, sample_data)
    return self._call_api(prompt)

# 3. 在 main.py 添加 UI 交互
```

#### 2. 添加新的数据源支持

```python
# 1. 在 core/ 创建新的 loader
class CSVLoader:
    def __init__(self, file_path: Union[str, Path]):
        pass
    
    def load(self) -> pd.DataFrame:
        pass

# 2. 在 main.py 添加文件类型判断
```

### 测试

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_data_profiler.py

# 运行并显示覆盖率
pytest --cov=core tests/
```

#### 编写测试

```python
# tests/test_data_profiler.py
import pytest
import pandas as pd
from core.data_profiler import DataProfiler

class TestDataProfiler:
    def test_numeric_column_profiling(self):
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        profiler = DataProfiler(df)
        profile = profiler.profile()
        
        assert profile.row_count == 5
        assert profile.column_count == 1
        assert profile.columns[0].dtype == '整数'
    
    def test_missing_value_detection(self):
        df = pd.DataFrame({'value': [1, None, 3, None, 5]})
        profiler = DataProfiler(df)
        profile = profiler.profile()
        
        assert profile.columns[0].null_count == 2
        assert profile.columns[0].null_ratio == 0.4
```

### 调试技巧

#### 1. 启用日志

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### 2. 使用 Streamlit 调试

```python
# 在 main.py 中添加调试信息
st.write("调试信息:", debug_variable)

# 使用 st.expander 折叠调试内容
with st.expander("调试信息"):
    st.json(data)
```

#### 3. API 调试

```python
# 在 ai_analyzer.py 中启用请求日志
logger.info("API 请求: %s", payload)
logger.info("API 响应: %s", response.json())
```

### 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

### 发布流程

```bash
# 1. 更新版本号
# 在 config.py 或 setup.py 中更新版本

# 2. 更新 CHANGELOG.md

# 3. 提交更改
git add .
git commit -m "Release v1.0.0"

# 4. 打标签
git tag -a v1.0.0 -m "Release v1.0.0"

# 5. 推送
git push origin main --tags
```

---

## 常见问题 FAQ

### Q1: 如何获取 DeepSeek API Key？

**A:** 
1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册并登录账号
3. 在 API Keys 页面创建新的 API Key
4. 复制 API Key 到 `.env` 文件

### Q2: 支持哪些 Excel 格式？

**A:** 目前支持：
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

CSV 格式支持计划在后续版本添加。

### Q3: 文件大小有限制吗？

**A:** 默认限制为 50MB，可通过环境变量调整：
```env
MAX_FILE_SIZE_MB=100  # 设置为 100MB
```

### Q4: 分析结果不准确怎么办？

**A:** 
1. 确保数据质量良好（无过多缺失值）
2. 尝试更清晰地描述你的问题
3. 提供更多上下文信息
4. 如果问题持续，请提交 Issue

### Q5: 如何提高分析速度？

**A:**
1. 减少数据量（筛选关键列）
2. 使用更快的网络连接
3. 调整 API 超时时间：
```env
API_TIMEOUT=120  # 增加超时时间
```

### Q6: 支持多语言吗？

**A:** 目前主要支持中文，AI 分析结果默认为中文输出。后续版本将添加多语言支持。

### Q7: 数据安全如何保障？

**A:**
1. 数据仅在本地处理，不会上传到第三方服务器
2. AI 分析通过 DeepSeek API 进行，遵循其隐私政策
3. API Key 通过环境变量管理，不会泄露
4. 建议不要上传敏感数据

### Q8: 如何部署到生产环境？

**A:** 详见 [DEPLOYMENT.md](DEPLOYMENT.md) 文档，支持：
- Streamlit Cloud（推荐，免费）
- Docker 部署
- 云服务器部署

### Q9: 遇到 "Rate Limit" 错误怎么办？

**A:** 
1. 等待一段时间后重试
2. 检查 API 额度是否用尽
3. 调整重试次数：
```env
API_MAX_RETRIES=5  # 增加重试次数
```

### Q10: 如何贡献代码？

**A:**
1. Fork 项目到你的 GitHub
2. 创建功能分支
3. 提交 Pull Request
4. 等待代码审查和合并

---

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

```
MIT License

Copyright (c) 2024 AI Excel Analyzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 联系方式

- **GitHub**: [ai-excel-analyzer](https://github.com/your-username/ai-excel-analyzer)
- **Issues**: [提交问题](https://github.com/your-username/ai-excel-analyzer/issues)
- **Email**: your-email@example.com

---

## 致谢

- [DeepSeek](https://deepseek.com/) - 提供 AI 能力支持
- [Streamlit](https://streamlit.io/) - 提供 Web 框架
- [pandas](https://pandas.pydata.org/) - 数据处理库
- [Jinja2](https://jinja.palletsprojects.com/) - 模板引擎

---

**如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！**
