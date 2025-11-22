# BiteBook 项目说明

一个基于 FastAPI 的PDF文档管理系统（列表、详情、CRUD、上传 PDF 生成封面）、文本解析与 AI 分析任务，并提供本地与 Vercel 部署方式。

## 技术栈

- 后端：FastAPI、SQLAlchemy、SQLite（本地开发使用）
- 前端：Vue 3、TypeScript、Vite、Element Plus、Vue Router
- 云函数：Vercel Serverless Functions（Python 3.11）

## 目录结构

```
bitebook/
├─ app/
│  ├─ api/               # 路由层（FastAPI）
│  │  └─ books.py
│  ├─ model/             # ORM 模型（SQLAlchemy）
│  │  └─ book.py
│  ├─ repository/        # 仓储层（数据访问）
│  │  └─ book_repository.py
│  ├─ schema/            # Pydantic 模式
│  │  └─ book.py
│  ├─ service/           # 领域服务（业务逻辑）
│  │  └─ book_service.py
│  ├─ static/            # OpenAPI 文档静态资源（本地）
│  │  ├─ swagger-ui/
│  │  │  ├─ swagger-ui.min.css
│  │  │  ├─ swagger-ui-bundle.js
│  │  │  └─ favicon.png
│  │  └─ redoc/
│  └─ main.py            # 应用入口（配置、CORS、文档路由、种子数据）
├─ api/
│  └─ index.py           # Vercel Python 函数入口，导出 FastAPI 应用
├─ front/                # 前端工程（Vue3 + TS + Element Plus）
│  ├─ src/
│  │  ├─ router/
│  │  │  └─ index.ts
│  │  ├─ services/
│  │  │  ├─ api.ts
│  │  │  └─ books.ts
│  │  ├─ types/
│  │  │  └─ book.ts
│  │  ├─ views/
│  │  │  ├─ BooksList.vue
│  │  │  └─ BookDetail.vue
│  │  ├─ App.vue
│  │  └─ main.ts
│  ├─ package.json
│  └─ vite.config.ts
├─ requirements.txt      # Vercel Python 函数依赖
├─ vercel.json           # Vercel 前后端一体化部署配置
├─ .vercelignore         # Vercel 上传忽略（根目录）
├─ pyproject.toml        # 后端依赖（FastAPI/SQLAlchemy/uvicorn 等）
├─ uv.lock
└─ main.py               # uvicorn 启动脚本（运行 app/main.py）
```

## 后端运行（本地）

要求 Python ≥ 3.13，推荐使用 uv 管理依赖。

1) 安装依赖并创建虚拟环境

```
uv sync
```

2) 启动开发服务（默认 8000 端口）

```
uv run python main.py
```

3) 访问接口与文档

- API 示例：`http://localhost:8000/api/books?page=1&page_size=10`
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

说明：文档页面使用本地静态资源，需确保以下文件存在：

- `app/static/swagger-ui/swagger-ui.min.css`
- `app/static/swagger-ui/swagger-ui-bundle.js`
- `app/static/redoc/redoc.standalone.js`

若缺失，请将对应构建产物拷贝到以上路径。

## 数据库（本地）

- 类型：SQLite 本地文件
- 位置：`./bitebook.db`
- 初始化：首次启动时会自动插入 10 条世界儿童文学经典书目的种子数据

若需重置数据，删除 `bitebook.db` 后重启后端即可。

提示：Vercel 无法持久化写入 SQLite 或本地文件，生产环境请替换为云数据库与对象存储（见下文“Vercel 部署”）。

## 后端 API 约定

- 创建图书

```
POST /api/books
Body JSON: {
  "title": "string",
  "author": "string",
  "description": "string?",
  "published_year": 2000?,
  "isbn": "string?"
}
```

- 获取详情

```
GET /api/books/{id}
```

- 列表查询（支持搜索与分页）

```
GET /api/books?q=keyword&page=1&page_size=20
```

- 更新图书

```
PUT /api/books/{id}
Body JSON: 与创建字段相同（均为可选）
```

- 删除图书

```
DELETE /api/books/{id}
```

注意：`isbn` 在服务层会进行唯一性校验，重复会返回 400。

- 启动分析任务

```
POST /api/books/{id}/analyze
```

- 查询文本

```
GET /api/books/{id}/texts?start=0&limit=50&page_number=1?
```

- 查询题目（含首条解析）

```
GET /api/books/{id}/questions?start=0&limit=50
```

## 前端运行（本地）

进入 `front` 目录：

```
cd front
npm install
npm run dev
```

默认运行在 `http://localhost:5173/`。

### 前端配置

- 后端地址可通过环境变量覆盖：`VITE_API_BASE`
  - 为空字符串时走同域 `/api/...`（适用于 Vercel 前后端同域部署）
  - 未设置时默认 `http://localhost:8000`
- 页面：
  - 列表页：`/books`（封面网格样式，搜索/分页）
  - 详情页：`/books/:id`
- UI 组件库：Element Plus
- 路由：Vue Router

### 响应式布局

- 内容区最大宽度 1024px，并针对 960px 与 700px 做收窄与间距调整
- 列表封面网格在不同断点下使用不同的最小列宽（180/160/140 px）以保持良好展示密度

## 常见问题

- 文档页面样式或脚本 404：请确认 `app/static` 下的资源路径与文件名一致
- 跨域问题：后端已启用 CORS，允许 `http://localhost:5173` 与 `http://127.0.0.1:5173`
- 依赖问题：后端使用 uv，前端使用 npm（或 pnpm）

## Vercel 部署

本仓库已配置前后端一体部署到 Vercel：

- 前端静态构建
  - 使用 `@vercel/static-build` 在云端执行：`cd front && npm ci && npm run build`
  - 构建产物目录：`front/dist`
- 后端 Python 函数
  - 入口：`api/index.py`（内容为 `from app.main import app`）
  - 运行时：Python 3.11（在 `vercel.json` 的 `functions` 指定）
- 路由重写
  - `rewrites`: `/api/(.*)` → `/api/index.py`
  - 其他路径 → `/index.html`（SPA 前端路由）
- 上传忽略
  - 根目录 `.vercelignore` 与 `front/.vercelignore` 排除 `node_modules`、构建产物与本地无关文件，避免上传上万文件

环境变量：

- 前端
  - `VITE_API_BASE` 建议设为空字符串，使用同域 API（示例 `""`）
- 后端（可选）
  - `DASHSCOPE_API_KEY`：启用阿里云通义模型；未设置时后端使用本地降级策略生成题目与摘要

生产注意事项：

- Vercel Serverless 是只读临时文件系统，无法持久化写入：
  - SQLite、`app/files`、`app/covers` 在云端不持久，上传与封面生成仅适用于本地开发
  - 建议替换为云数据库（如 Postgres/Neon/Supabase）与对象存储（S3/OSS/Blob Storage），并在 `app/config.py` 中改用外部连接串

部署步骤：

1) 将仓库推送到 GitHub/GitLab
2) 在 Vercel 导入仓库，确认使用根目录的 `vercel.json`
3) 在 Vercel 项目设置添加环境变量（至少前端 `VITE_API_BASE`）
4) 触发部署，前端构建与后端函数将自动上线

本地点击部署时若上传文件数很多（如 15000+），请确保部署目录存在 `.vercelignore`（我们已在根与 `front/` 添加）以排除 `node_modules` 等不必要内容。

## Git 推送提示

若出现 `error: src refspec main does not match any`：

- 初始化并推送到 `main`：

```
git add -A
git commit -m "chore: initial commit"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

- 若当前分支非 `main`，重命名后再推送：`git branch -M main && git push -u origin main`

## 开发约定

- 后端分层结构：`api → service → repository → model → schema`
- 统一使用 Pydantic 校验请求体与响应模型
- 仓储层负责 SQLAlchemy 的会话与 CRUD；服务层包含领域校验（如 `isbn` 唯一）

---

如需拓展（创建/编辑界面、上传封面、更多筛选条件等），可在现有分层基础上继续演进，前端按 Element Plus 风格追加交互组件与表单即可。
