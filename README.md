# 护理教学智能体

面向护理科研与教学场景的智能问答系统，基于 **Coze AI** 工作流与 **Neo4j** 知识图谱，提供带领域知识支撑的对话与检索能力。前端为单页 Web 应用，后端为 FastAPI 服务，支持本地运行与云部署（如 Vercel）。

---

## 快速开始

### 环境要求

- **Python**：3.10 或更高版本（建议使用 3.11+，可从 [python.org](https://www.python.org/) 安装，安装时勾选「Add Python to PATH」）。
- **包管理**：使用 `pip`（通常随 Python 安装）；可选使用虚拟环境（`venv` / `conda`）以隔离依赖。

### 安装与运行

**方式一：一键启动（推荐）**

在项目根目录（包含 `run.py` 与 `requirements.txt` 的目录）下打开终端，执行：

```bash
python run.py
```

脚本会检查 Python 版本与依赖，必要时提示安装依赖，然后启动服务。

**方式二：手动安装后启动**

若已确认环境，可先安装依赖再直接启动应用：

```bash
pip install -r requirements.txt
python app.py
```

或使用 uvicorn 指定主机与端口：

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 访问地址

- **本地**：<http://localhost:8000>
- **在线演示**：[nursingresearchagent.vercel.app](https://nursingresearchagent.vercel.app/)

---

## 配置

运行前需配置 **Coze** 与（可选）**Neo4j** 相关环境变量；未配置时部分功能不可用（见下方说明）。

### 环境变量说明

| 变量名 | 说明 | 必填 | 获取方式 |
|--------|------|------|----------|
| `COZE_API_TOKEN` | Coze 开放平台个人访问令牌，用于调用 Workflow API | 是（聊天功能） | [Coze 个人访问令牌](https://www.coze.com/open/oauth/pats) 创建并复制 |
| `COZE_WORKFLOW_ID` | 已发布的 Coze 工作流 ID | 是（聊天功能） | Coze 控制台 → 对应工作流 → 详情中的工作流 ID |
| `COZE_BOT_ID` | Coze 机器人 ID（若工作流未绑定可留空） | 否 | 按需在 Coze 控制台查看 |
| `NEO4J_URI` | Neo4j 连接 URI（如 `neo4j+s://xxx.databases.neo4j.io`） | 知识卡片/搜索功能需要 | Neo4j Aura 或自建实例 |
| `NEO4J_USERNAME` | Neo4j 用户名 | 同上 | 实例创建时设定 |
| `NEO4J_PASSWORD` | Neo4j 密码 | 同上 | 实例创建时设定 |
| `NEO4J_DATABASE` | 数据库名，通常为 `neo4j` | 否（有默认值） | 默认 `neo4j` |

### 配置方式

- **本地开发**：在项目根目录新建 `.env` 文件（不要提交到 Git），按 `KEY=value` 逐行填写；或直接修改代码中的默认值（仅限本地调试）。
- **生产 / 云部署**：在 Vercel、Render 等平台的项目设置中添加上述环境变量；敏感信息勿写入代码仓库。

配置优先级：环境变量 > 代码内默认值。生产环境建议全部使用环境变量，避免在代码中写死密钥。

---

## API

服务默认以 JSON 交互，根路径返回前端页面；以下为后端主要接口摘要。

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 返回前端单页 `index.html` |
| `/chat` | POST | 聊天对话：请求体 `{"message": "用户输入"}`，返回 `{"response": "AI 回复文本"}` |
| `/cards` | GET | 从 Neo4j 拉取知识卡片结构，返回 JSON 数组；依赖 Neo4j 配置 |
| `/search` | GET | 知识图谱搜索，查询参数 `query=关键词`，返回匹配节点与关系 |
| `/health` | GET | 健康检查，返回 `{"status": "healthy", ...}` |

请求示例（聊天）：

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是 t 检验？"}'
```

## 部署

- **Vercel**：导入项目 → Root: `./`，Build: `pip install -r requirements.txt` → 配置环境变量

## 常见问题（FAQ）

---

**Q：这个项目到底是干什么用的？和普通聊天机器人有什么区别？**

A：本项目是面向**护理科研与教学场景**的智能问答系统，而不是通用闲聊机器人。它背后接入了 **Coze Workflow** 与 **Neo4j 知识图谱**：前者负责自然语言理解与生成，后者提供护理研究领域的概念、统计方法、研究设计等结构化知识。因此，当你询问「t 检验的适用条件」「质性研究常用方法」等问题时，系统会结合图谱中的节点与关系生成更准确、可追溯的答案。简而言之：**用途是护理教学与科研辅导，差异在于有领域知识图谱支撑**。

---

**Q：我完全没有编程基础，也不想装 Python，能用吗？**

A：可以。若仅希望**使用**而不自行部署，可直接访问已部署的在线版 [nursingresearchagent.vercel.app](https://nursingresearchagent.vercel.app/)，在浏览器中提问即可，无需安装任何环境。  
若希望**在本地或自己的机器上运行**，则需要：  
1）安装 Python 3.10 或更高版本（从 [python.org](https://www.python.org/) 下载并勾选「Add to PATH」）；  
2）在项目目录下打开终端（或命令提示符），依次执行 `pip install -r requirements.txt` 与 `python run.py`；  
3）在浏览器访问提示的地址（一般为 http://localhost:8000）。  
不熟悉命令行的话，建议优先使用在线版；本地运行适合需要自定义配置或内网部署的场景。

---

**Q：Coze Token 是什么？必须填吗？在哪里填？**

A：**Coze Token**（个人访问令牌）是调用 Coze 开放平台 API 时的身份凭证，用于鉴权并计费。本项目中的对话与工作流调用都依赖该 Token，**未配置或配置错误时，聊天功能将无法使用**（前端可能报错或一直处于「思考中」）。  
获取方式：登录 [Coze 开放平台](https://www.coze.com) → 进入 [个人访问令牌页面](https://www.coze.com/open/oauth/pats) → 创建新令牌并复制。  
填写位置取决于运行方式：**本地运行**时可在项目目录下新建 `.env` 文件，写入 `COZE_API_TOKEN=你的令牌`，或直接修改代码中的默认配置（不推荐提交到版本库）；**Vercel / Render 等云部署**时在对应平台的项目设置 → Environment Variables 中添加同名变量即可。同时需配置 `COZE_WORKFLOW_ID`（在 Coze 工作流详情页可查），`COZE_BOT_ID` 为可选项。

---

**Q：没有 Neo4j 数据库怎么办？能只用一个 Coze 吗？**

A：本系统的**知识卡片**（左侧栏）与 **图谱搜索** 接口（`/search`）依赖 Neo4j 中已导入的护理研究知识图谱数据；**对话接口**（`/chat`）则主要依赖 Coze Workflow，Workflow 内部可再选择是否调用 Neo4j 做检索增强。  
因此：若**仅有 Coze 配置、未配置或无法连接 Neo4j**，聊天功能在 Workflow 不依赖图谱的情况下仍可使用，但**侧边栏知识卡片会加载失败**，`/cards` 与 `/search` 可能返回错误或空数据。若希望完整使用所有功能，需要自建或使用云版 Neo4j（如 [Neo4j Aura](https://neo4j.com/cloud/aura/) 免费实例），并将图谱数据按项目所需 schema 导入后，在环境变量中配置 `NEO4J_URI`、`NEO4J_USERNAME`、`NEO4J_PASSWORD`、`NEO4J_DATABASE`。

---

**Q：运行时报错「ModuleNotFoundError: No module named 'xxx'」或类似找不到模块，怎么解决？**

A：这类错误表示当前 Python 环境中**缺少项目依赖**。请先确认已进入项目根目录（包含 `requirements.txt` 的目录），在终端执行：  
`pip install -r requirements.txt`  
等待安装完成后，再执行 `python run.py` 或 `python app.py`。  
若仍报错，可检查：1）使用的是否为 Python 3.10+（运行 `python --version`）；2）是否在虚拟环境中（若有 venv/conda，需先激活再安装与运行）；3）是否存在多版本 Python 导致 `pip` 与 `python` 不对应，可改为 `python -m pip install -r requirements.txt` 再 `python run.py`。

---

**Q：可以部署到自己的服务器或内网吗？和用 Vercel 有什么区别？**

A：可以。本项目为常规 FastAPI 应用，可在任何能运行 Python 的服务器（Linux / Windows 等）上部署。典型步骤：在服务器上克隆仓库 → 安装 Python 3.10+ 与依赖（`pip install -r requirements.txt`）→ 配置环境变量（Coze、Neo4j 等）→ 使用 `python app.py` 直接运行，或通过 **uvicorn** / **gunicorn** 作为生产 WSGI/ASGI 服务运行（例如 `uvicorn app:app --host 0.0.0.0 --port 8000`）。若需内网访问，确保防火墙放行对应端口，或搭配 Nginx 做反向代理与 HTTPS。  
与 Vercel 的区别：**自建服务器**可完全掌控数据与网络、适合内网或对合规有要求的场景，但需自行维护系统与安全；**Vercel** 则免运维、自动 HTTPS 与全球 CDN，适合公网演示或轻量使用，依赖其运行时的限制（如冷启动、执行时长等）。可按实际需求选择部署方式。

## 许可证

MIT License
