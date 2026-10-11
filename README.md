# 护理科研教学智能体

**Nursing Research & Teaching Intelligent Agent** - 基于 Coze AI 和 Neo4j 知识图谱的护理教学辅助系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Coze](https://img.shields.io/badge/AI-Coze-purple.svg)](https://www.coze.com)

## 🎯 项目简介

护理科研教学智能体是专为护理专业科研和教学场景设计的AI助手系统。通过 **Coze AI** 和 **Neo4j 知识图谱**，为用户提供专业、结构化的教学回答。

### ✨ 核心特性

- 🤖 **Coze AI 集成**: 基于 Coze Workflow API 的智能问答
- 📚 **Neo4j 知识图谱**: 护理研究专业知识体系
- 🎨 **响应式界面**: 完美适配桌面端和移动端
- 📖 **Markdown 渲染**: 支持链接、表格等丰富格式

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip 包管理器

### 安装与运行

```bash
# 一键启动（推荐）
python run.py

# 或手动启动
pip install -r requirements.txt
python app.py
```

访问：http://localhost:8000

## 🔧 配置说明

### 环境变量配置（推荐）

在部署平台或 `.env` 文件中配置：

```bash
# Coze OAuth JWT 配置（在 www.coze.com 创建服务类 OAuth 应用）
COZE_OAUTH_APP_ID=your-oauth-app-id
COZE_OAUTH_KEY_ID=your-public-key-fingerprint
COZE_OAUTH_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
COZE_WORKFLOW_ID=your-workflow-id
COZE_BOT_ID=your-bot-id  # 可选

# Neo4j 配置
NEO4J_URI=neo4j+s://your-neo4j-instance
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
```

### 本地开发

项目也可直接读取 `coze_oauth_python_jwt/coze_oauth_config.json`。如果此文件存在，上述三个 OAuth 环境变量可以不设置；环境变量优先于文件中的对应字段。工作流 ID 保持现有值。私钥环境变量可以填真实换行，也可以用 `\n` 表示换行。Neo4j 仍使用原有配置。

### Vercel 自动获取 Coze 令牌

1. 在 **www.coze.com** 的 Personal 空间进入 API Management → Authorization → OAuth Apps，创建一个新的 **Normal / Service Application**，用于本项目。只授权当前工作流所在工作区及调用 Workflow.run 所需权限。
2. 创建密钥后保存下载的 RSA 私钥，并记下 App ID 与公钥指纹（Key ID）。不要复用其他项目的 OAuth 应用。
3. 当前项目已放入 `coze_oauth_python_jwt/coze_oauth_config.json`。如果使用这份配置，将该目录随项目提交并部署到 Vercel 即可；如果不随代码部署，则在 Vercel **Settings → Environment Variables** 中设置 `COZE_OAUTH_APP_ID`、`COZE_OAUTH_KEY_ID` 和 `COZE_OAUTH_PRIVATE_KEY`，然后重新部署。`COZE_WORKFLOW_ID` 无需改变。无需再设置 `COZE_API_TOKEN`。
4. 服务会在首次请求或令牌到期前约五分钟签署新的 JWT，自动换取最长 86399 秒的访问令牌。Vercel 无请求时不会运行续期任务；下一次请求会自行换取新令牌。

当前 API 地址是 `api.coze.com`，所以 OAuth 应用必须建在 `www.coze.com`。如果工作流实际上属于 `www.coze.cn`，需要同时调整 API 地址、JWT audience 和 OAuth 应用所属站点。

## 📡 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/chat` | POST | 聊天对话接口 |
| `/cards` | GET | 获取知识卡片 |
| `/search` | GET | 知识图谱搜索 |
| `/health` | GET | 健康检查 |

### 使用示例

```bash
# 聊天接口
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "什么是t检验？"}'

# 知识搜索
curl "http://localhost:8000/search?query=护理研究"
```

## 📁 项目结构

```
NursingEdu-Agent/
├── app.py                 # FastAPI 后端主文件
├── index.html             # 前端界面
├── run.py                 # 启动脚本
├── requirements.txt       # 依赖包列表
└── vercel.json           # Vercel 部署配置
```

## 📦 技术栈

- **后端**: FastAPI + Python 3.10+
- **AI**: Coze Workflow API
- **知识图谱**: Neo4j
- **前端**: HTML5 + CSS3 + JavaScript
- **部署**: Vercel / Render

## 📦 主要依赖

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
requests==2.31.0
neo4j==5.14.1
```

## 🌐 部署

### Vercel 部署

1. 在 Vercel 中导入项目
2. Framework Preset: **Other**
3. Root Directory: `./`
4. Build Command: `pip install -r requirements.txt`
5. 配置环境变量
6. 部署

### Render 部署

1. 连接 GitHub 仓库
2. 选择 Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python run.py`
5. 配置环境变量
6. 部署

## ⚠️ 注意事项

- 确保网络连接正常，以便调用外部 API
- 需要配置有效的 API 密钥才能正常使用
- 建议在 Python 3.10+ 环境下运行

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📄 许可证

MIT License

---

*护理科研教学智能体 - 让AI助力护理教育* 🏥📚
