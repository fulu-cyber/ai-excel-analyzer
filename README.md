<h1 align="center">AI Excel Analyzer 📊</h1>

<p align="center">
  <strong>AI 驱动的智能 Excel 数据分析工具</strong>
  <br>
  上传 Excel 文件，AI 自动生成数据概览、分析洞察和报告
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Streamlit-1.28+-red" alt="Streamlit 1.28+">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
</p>

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 📁 **Excel 文件读取** | 支持 `.xlsx` / `.xls` 格式，自动识别 Sheet |
| 📊 **AI 数据概览** | 上传后自动生成数据摘要和结构分析 |
| 🔍 **智能分析洞察** | 趋势分析、异常检测、关联分析、业务建议 |
| 💬 **自然语言查询** | 用中文提问，AI 结合数据回答（如"哪个产品销量最高？"） |
| 📄 **一键生成报告** | Markdown 格式分析报告，可复制或下载 |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/fulu-cyber/ai-excel-analyzer.git
cd ai-excel-analyzer
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
# 复制配置模板
cp .env.example .env
```

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=sk-your-api-key-here
```

> 获取 API Key：[DeepSeek 平台](https://platform.deepseek.com/)

### 4. 启动应用

```bash
streamlit run main.py
```

打开浏览器访问 `http://localhost:8501` 即可使用。

## 使用流程

1. **上传文件** — 选择 `.xlsx` 或 `.xls` 文件（大小限制 50MB）
2. **查看概览** — 自动生成数据规模、字段类型、质量评分
3. **AI 分析** — 点击"开始分析"，获取趋势、异常、业务建议
4. **提问数据** — 在聊天框输入自然语言问题，AI 即时回答
5. **生成报告** — 一键输出完整的分析报告

## 技术栈

| 组件 | 技术 |
|------|------|
| 编程语言 | Python 3.9+ |
| Web 框架 | Streamlit |
| 数据处理 | pandas, openpyxl, xlrd |
| AI 能力 | DeepSeek API |
| 模板引擎 | Jinja2 |
| 环境管理 | python-dotenv |

## 项目结构

```
ai-excel-analyzer/
├── main.py                     # Streamlit 主入口
├── config.py                   # 配置管理
├── requirements.txt            # 依赖清单
├── core/
│   ├── excel_loader.py         # Excel 文件读取
│   ├── data_profiler.py        # 数据画像生成
│   ├── ai_analyzer.py          # AI 分析核心
│   ├── prompt_templates.py     # 提示词模板
│   └── report_generator.py     # 报告生成
├── utils/
│   └── data_processor.py       # 数据预处理
└── .streamlit/
    └── config.toml             # Streamlit 配置
```

## FAQ

**Q：如何获取 DeepSeek API Key？**
A：访问 [platform.deepseek.com](https://platform.deepseek.com/) 注册并创建 API Key。

**Q：支持哪些文件格式？**
A：支持 `.xlsx` 和 `.xls`，CSV 支持计划后续添加。

**Q：有文件大小限制吗？**
A：默认 50MB，可通过环境变量 `MAX_FILE_SIZE_MB` 调整。

**Q：数据安全吗？**
A：数据在本地处理，仅通过 DeepSeek API 发送数据摘要用于分析，不会存储你的文件。

**Q：如何部署到服务器？**
A：详见 [DEPLOYMENT.md](DEPLOYMENT.md)，支持 Streamlit Cloud 免费部署。

## 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

<p align="center">
  如果这个项目对你有帮助，请 ⭐ Star 支持一下！
  <br>
  <a href="https://github.com/fulu-cyber/ai-excel-analyzer/issues">提交 Issue</a>
</p>
