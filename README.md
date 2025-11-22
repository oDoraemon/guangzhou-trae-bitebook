# BiteBook 项目说明

一个基于 FastAPI 的读书应用后端 + Vue3/TypeScript/Element Plus 前端示例，实现基础的图书管理（列表、详情、CRUD）以及本地 OpenAPI 文档静态资源加载。

## 技术栈

- 后端：FastAPI、SQLAlchemy、SQLite（本地文件）
- 前端：Vue 3、TypeScript、Vite、Element Plus、Vue Router

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
├─ pyproject.toml        # 后端依赖（FastAPI/SQLAlchemy/uvicorn 等）
├─ uv.lock
└─ main.py               # uvicorn 启动脚本（运行 app/main.py）
```

## 后端运行

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

## 数据库

- 类型：SQLite 本地文件
- 位置：`./bitebook.db`
- 初始化：首次启动时会自动插入 10 条世界儿童文学经典书目的种子数据

若需重置数据，删除 `bitebook.db` 后重启后端即可。

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

## 前端运行

进入 `front` 目录：

```
cd front
npm install
npm run dev
```

默认运行在 `http://localhost:5173/`。

### 前端配置

- 后端地址可通过环境变量覆盖：`VITE_API_BASE`（默认 `http://localhost:8000`）
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

## 开发约定

- 后端分层结构：`api → service → repository → model → schema`
- 统一使用 Pydantic 校验请求体与响应模型
- 仓储层负责 SQLAlchemy 的会话与 CRUD；服务层包含领域校验（如 `isbn` 唯一）

---

如需拓展（创建/编辑界面、上传封面、更多筛选条件等），可在现有分层基础上继续演进，前端按 Element Plus 风格追加交互组件与表单即可。
