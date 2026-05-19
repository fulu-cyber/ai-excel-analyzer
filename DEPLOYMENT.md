# AI Excel Analyzer 部署指南

本文档详细说明如何将 AI Excel Analyzer 应用部署到 Streamlit Cloud。

## 前置条件

1. 拥有 GitHub 账号
2. 项目代码已推送到 GitHub 仓库
3. 拥有 DeepSeek API Key（用于 AI 分析功能）

## 部署步骤

### 1. 准备项目文件

确保项目根目录包含以下文件：

```
ai-excel-analyzer/
├── main.py                    # 主应用入口
├── config.py                  # 配置文件
├── requirements.txt           # Python 依赖
├── core/                      # 核心模块
├── utils/                     # 工具模块
├── .streamlit/
│   └── config.toml           # Streamlit 配置
└── Procfile                   # 可选，用于其他平台
```

### 2. 推送代码到 GitHub

```bash
# 初始化 Git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "准备部署到 Streamlit Cloud"

# 添加远程仓库
git remote add origin https://github.com/fulu-cyber/ai-excel-analyzer.git

# 推送到 GitHub
git push -u origin main
```

### 3. 部署到 Streamlit Cloud

1. 访问 [Streamlit Cloud](https://share.streamlit.io/)
2. 使用 GitHub 账号登录
3. 点击 **New app** 按钮
4. 填写部署信息：
   - **Repository**: 选择你的仓库 `ai-excel-analyzer`
   - **Branch**: `main`
   - **Main file path**: `main.py`
5. 点击 **Deploy!** 开始部署

### 4. 配置环境变量（API Key）

部署完成后，需要配置 DeepSeek API Key：

1. 在 Streamlit Cloud 的应用管理页面
2. 点击右上角的 **⋮** (更多选项)
3. 选择 **Settings**
4. 找到 **Secrets** 部分
5. 点击 **Edit** 编辑密钥
6. 添加以下配置：

```toml
DEEPSEEK_API_KEY = "sk-your-api-key-here"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-flash"
```

7. 点击 **Save** 保存
8. 应用会自动重启并加载新的密钥

## 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 空 | 是（AI功能必需） |
| `DEEPSEEK_BASE_URL` | API 基础 URL | `https://api.deepseek.com` | 否 |
| `DEEPSEEK_MODEL` | 使用的模型 | `deepseek-chat` | 否 |
| `MAX_FILE_SIZE_MB` | 最大文件大小(MB) | `50` | 否 |
| `API_TIMEOUT` | API 超时时间(秒) | `60` | 否 |
| `API_MAX_RETRIES` | API 最大重试次数 | `3` | 否 |

## 配置文件说明

### .streamlit/config.toml

此文件配置 Streamlit 应用的外观和行为：

```toml
[theme]
primaryColor = "#6366f1"      # 主题色
backgroundColor = "#0f172a"   # 背景色
secondaryBackgroundColor = "#1e293b"  # 次要背景色
textColor = "#f1f5f9"         # 文字颜色
font = "sans serif"           # 字体

[server]
headless = true               # 无头模式
port = 8501                   # 端口
enableCORS = false            # 禁用 CORS
enableXsrfProtection = true   # 启用 XSRF 保护
maxUploadSize = 50            # 最大上传大小(MB)

[browser]
gatherUsageStats = false      # 不收集使用统计
```

## 常见问题

### Q: 部署后无法访问怎么办？

A: 检查以下几点：
- 确认 `requirements.txt` 包含所有依赖
- 确认 `main.py` 路径正确
- 查看 Streamlit Cloud 的日志输出

### Q: AI 分析功能不工作？

A: 检查以下几点：
- 确认已在 Streamlit Cloud 的 Secrets 中配置了 `DEEPSEEK_API_KEY`
- 确认 API Key 有效且有足够额度
- 检查网络是否能访问 DeepSeek API

### Q: 上传大文件失败？

A: 检查以下几点：
- 默认最大上传大小为 50MB
- 可在 `.streamlit/config.toml` 中修改 `maxUploadSize`
- Streamlit Cloud 对免费版有内存限制

### Q: 如何更新已部署的应用？

A: 只需将代码推送到 GitHub 仓库，Streamlit Cloud 会自动检测并重新部署：

```bash
git add .
git commit -m "更新功能"
git push
```

## 部署检查清单

部署前请确认以下事项：

- [ ] 代码已推送到 GitHub
- [ ] `requirements.txt` 包含所有依赖
- [ ] `main.py` 是应用入口文件
- [ ] `.streamlit/config.toml` 配置正确
- [ ] 敏感信息（如 API Key）不在代码中
- [ ] `.gitignore` 包含 `.env` 和 `secrets.toml`

部署后请确认：

- [ ] 应用可以正常访问
- [ ] 文件上传功能正常
- [ ] AI 分析功能正常（需配置 API Key）
- [ ] 报告生成功能正常
- [ ] 样式显示正确

## 其他部署选项

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 添加 API Key

# 运行应用
streamlit run main.py
```

### Docker 部署

如需使用 Docker 部署，可以创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.headless=true"]
```

## 获取帮助

如遇到问题，请检查：
- [Streamlit 官方文档](https://docs.streamlit.io/)
- [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-community-cloud)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs)

---

*最后更新: 2026-05-19*
