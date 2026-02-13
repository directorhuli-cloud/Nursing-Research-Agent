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
# Coze API 配置
COZE_API_TOKEN=your-coze-api-token
COZE_WORKFLOW_ID=your-workflow-id
COZE_BOT_ID=your-bot-id  # 可选

# Neo4j 配置
NEO4J_URI=neo4j+s://your-neo4j-instance
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
```

### 本地开发

配置已包含默认值，可直接运行。生产环境建议使用环境变量。

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
