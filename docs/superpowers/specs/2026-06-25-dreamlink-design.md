# DreamLink 视频网站设计文档

## 1. 项目概述

DreamLink 是一个仿哔哩哔哩的视频网站，面向普通用户、内容创作者和平台管理员，提供视频上传播放、用户系统、内容发现、评论互动和基础内容审核能力。

本设计文档用于指导第一阶段到可运行版本的实现。当前仓库尚未包含实际前后端源码，因此本文描述的是目标系统设计和落地约束，不代表已有实现。

### 1.1 目标

- 用户可以注册、登录、查看和编辑个人资料。
- 用户可以上传视频、填写视频信息、查看视频详情并播放视频。
- 用户可以浏览首页推荐、按分区筛选、搜索视频和查看排行榜。
- 用户可以对视频评论、点赞、收藏和投币。
- 管理员可以审核视频、管理用户、处理举报和查看基础统计。
- 系统可以通过 Docker Compose 在本地或单机服务器上部署运行。

### 1.2 非目标

- 第一阶段不实现复杂推荐算法，首页推荐先使用规则排序。
- 第一阶段不实现实时弹幕服务，可预留播放器入口，后续再做弹幕数据模型和 WebSocket。
- 第一阶段不实现大型对象存储，视频和封面先落本地文件系统，后续可替换为 S3/OSS/MinIO。
- 第一阶段不实现复杂私信、动态、直播、会员、支付和创作者收益体系。

### 1.3 角色

| 角色 | 说明 | 主要能力 |
| --- | --- | --- |
| 游客 | 未登录访问者 | 浏览公开视频、搜索、查看评论 |
| 普通用户 | 已注册登录用户 | 评论、点赞、收藏、投币、举报 |
| 创作者 | 普通用户的一种使用场景 | 上传视频、编辑自己发布的视频 |
| 管理员 | 后台运营人员 | 审核视频、处理举报、封禁用户 |
| 超级管理员 | 最高权限管理员 | 管理管理员账号和系统配置 |

## 2. 技术栈

### 2.1 前端

- Vue 3 + TypeScript
- Vite 构建工具
- Pinia 状态管理
- Vue Router 路由
- Axios 或 Fetch API 请求封装
- Vitest 单元测试
- 毛玻璃渐变 + 流星划过视觉风格（后期实现）

### 2.2 后端

- Python 3.11+
- FastAPI Web 框架
- SQLAlchemy 2.0 ORM
- Alembic 数据库迁移
- Pydantic 数据验证
- python-jose JWT 认证
- passlib 密码哈希
- pytest + httpx 测试

### 2.3 数据库与存储

- PostgreSQL 15+
- 本地文件系统保存上传视频和封面
- Nginx 提供静态文件访问

### 2.4 部署

- Docker Compose
- Nginx 反向代理
- 前端静态资源容器
- 后端 API 容器
- PostgreSQL 数据库容器

## 3. 整体架构

```
┌────────────────────┐
│  Browser / Client  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│       Nginx        │
│ 静态资源 / API代理  │
└──────┬───────┬─────┘
       │       │
       ▼       ▼
┌──────────┐ ┌────────────────┐
│ Frontend │ │ Backend API    │
│ Vue 3    │ │ FastAPI        │
└──────────┘ └───────┬────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌────────────────┐     ┌────────────────┐
│ PostgreSQL     │     │ Local Storage  │
│ 业务数据        │     │ 视频/封面文件    │
└────────────────┘     └────────────────┘
```

### 3.1 分层职责

| 层级 | 职责 |
| --- | --- |
| 前端页面层 | 页面渲染、路由跳转、表单校验、播放器交互 |
| 前端状态层 | 当前用户、Token、全局加载态和部分页面缓存 |
| API 路由层 | 请求入参校验、鉴权、响应格式封装 |
| Service 层 | 业务规则、权限判断、事务边界 |
| Model 层 | SQLAlchemy 数据模型和数据库关系 |
| Storage 层 | 上传文件保存、路径生成、文件类型和大小校验 |

## 4. 核心业务流程

### 4.1 注册登录流程

1. 用户提交用户名、邮箱和密码。
2. 后端校验用户名和邮箱唯一性。
3. 密码使用 passlib 哈希后保存。
4. 登录成功后返回 Access Token 和 Refresh Token。
5. 前端保存 Token，并在后续 API 请求中携带 `Authorization: Bearer <token>`。

### 4.2 视频上传流程

1. 用户选择视频文件和封面图，填写标题、简介、分区和标签。
2. 前端先做文件大小、格式和必填项校验。
3. 后端再次校验文件类型、文件大小、标题长度和用户权限。
4. 后端保存视频文件和封面文件，创建 `Video` 与至少一个 `VideoPart`。
5. 新视频默认进入 `pending` 状态，审核通过后变为 `published`。
6. 管理员在后台审核视频，拒绝时填写原因。

### 4.3 视频播放流程

1. 用户进入视频详情页。
2. 前端请求视频详情、分 P 列表和互动状态。
3. 后端仅返回 `published` 视频；作者和管理员可查看自己的非公开视频。
4. 播放器按当前分 P 的文件 URL 播放。
5. 首次有效播放时增加播放量，具体防刷策略第一阶段可按 IP + 用户 + 时间窗口做简单限制。

### 4.4 评论流程

1. 登录用户提交评论内容。
2. 后端校验视频存在且已发布、评论内容非空且不超过长度限制。
3. 一级评论 `parent_id` 为空；回复评论 `parent_id` 指向一级评论。
4. 删除评论第一阶段采用软删除，保留楼层结构并隐藏正文。

### 4.5 管理审核流程

1. 管理员登录后台。
2. 管理员查看待审核视频列表。
3. 管理员执行通过、拒绝或下架操作。
4. 后端记录审核操作人、审核时间和原因。
5. 视频状态变化后影响前台可见性。

## 5. 数据模型

### 5.1 通用约定

- 主键使用自增整数或 UUID，第一阶段优先使用自增整数，便于调试。
- 所有核心表包含 `created_at` 和 `updated_at`。
- 涉及删除且需要保留历史的数据优先使用软删除字段 `deleted_at`。
- 所有外键字段建立索引。
- 用户行为表对同一用户同一视频建立唯一约束，避免重复点赞、收藏。

### 5.2 核心实体

#### User（用户）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 用户 ID |
| username | varchar(32) | unique, not null | 用户名 |
| email | varchar(255) | unique, not null | 邮箱 |
| password_hash | varchar(255) | not null | 密码哈希 |
| avatar | varchar(500) | nullable | 头像路径 |
| bio | varchar(300) | nullable | 个人简介 |
| is_active | boolean | default true | 是否可登录 |
| is_banned | boolean | default false | 是否被封禁 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

#### Video（视频）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 视频 ID |
| title | varchar(100) | not null | 标题 |
| description | text | nullable | 描述 |
| cover | varchar(500) | not null | 封面路径 |
| duration | integer | default 0 | 总时长，单位秒 |
| view_count | integer | default 0 | 播放量 |
| like_count | integer | default 0 | 点赞数 |
| favorite_count | integer | default 0 | 收藏数 |
| coin_count | integer | default 0 | 投币数 |
| author_id | integer | FK users.id | 作者 ID |
| category_id | integer | FK categories.id | 分区 ID |
| status | enum | not null | `pending` / `published` / `rejected` / `offline` |
| reject_reason | varchar(300) | nullable | 审核拒绝原因 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

#### VideoPart（视频分 P）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 分 P ID |
| video_id | integer | FK videos.id | 视频 ID |
| title | varchar(100) | not null | 分 P 标题 |
| file_path | varchar(500) | not null | 视频文件路径 |
| duration | integer | default 0 | 分 P 时长，单位秒 |
| file_size | bigint | not null | 文件大小 |
| order | integer | not null | 排序，从 1 开始 |
| created_at | datetime | not null | 创建时间 |

#### Comment（评论）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 评论 ID |
| user_id | integer | FK users.id | 评论用户 |
| video_id | integer | FK videos.id | 视频 ID |
| parent_id | integer | FK comments.id, nullable | 父评论 ID |
| content | varchar(1000) | not null | 评论内容 |
| is_deleted | boolean | default false | 是否已删除 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

#### Like（点赞）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 点赞 ID |
| user_id | integer | FK users.id | 用户 ID |
| video_id | integer | FK videos.id | 视频 ID |
| created_at | datetime | not null | 创建时间 |

唯一约束：`(user_id, video_id)`。

#### FavoriteFolder（收藏夹）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 收藏夹 ID |
| user_id | integer | FK users.id | 用户 ID |
| name | varchar(50) | not null | 收藏夹名称 |
| is_default | boolean | default false | 是否默认收藏夹 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

#### Favorite（收藏）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 收藏 ID |
| user_id | integer | FK users.id | 用户 ID |
| video_id | integer | FK videos.id | 视频 ID |
| folder_id | integer | FK favorite_folders.id | 收藏夹 ID |
| created_at | datetime | not null | 创建时间 |

唯一约束：`(user_id, video_id, folder_id)`。

#### Coin（投币）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 投币 ID |
| user_id | integer | FK users.id | 用户 ID |
| video_id | integer | FK videos.id | 视频 ID |
| amount | integer | not null | 数量，取值 1 或 2 |
| created_at | datetime | not null | 创建时间 |

第一阶段不做真实币余额体系，只记录投币行为和数量；同一用户同一视频最多投 2 个币。

#### Admin（管理员）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 管理员 ID |
| username | varchar(32) | unique, not null | 用户名 |
| password_hash | varchar(255) | not null | 密码哈希 |
| role | enum | not null | `super_admin` / `reviewer` / `operator` |
| is_active | boolean | default true | 是否可登录 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

#### Category（分区）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 分区 ID |
| name | varchar(50) | unique, not null | 分区名称 |
| description | varchar(300) | nullable | 描述 |
| order | integer | default 0 | 排序 |
| is_active | boolean | default true | 是否启用 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

#### Report（举报）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 举报 ID |
| reporter_id | integer | FK users.id | 举报人 ID |
| target_id | integer | not null | 被举报内容 ID |
| target_type | enum | not null | `video` / `comment` / `user` |
| reason | varchar(300) | not null | 举报原因 |
| status | enum | not null | `pending` / `processed` / `dismissed` |
| handled_by | integer | FK admins.id, nullable | 处理人 |
| handled_at | datetime | nullable | 处理时间 |
| created_at | datetime | not null | 创建时间 |

#### AuditLog（审核日志）

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | integer | PK | 日志 ID |
| admin_id | integer | FK admins.id | 操作管理员 |
| target_type | varchar(30) | not null | 操作对象类型 |
| target_id | integer | not null | 操作对象 ID |
| action | varchar(50) | not null | 操作 |
| reason | varchar(300) | nullable | 原因 |
| created_at | datetime | not null | 创建时间 |

### 5.3 实体关系

- User 1:N Video
- User 1:N Comment
- Video 1:N VideoPart
- Video 1:N Comment
- Category 1:N Video
- User N:N Video，通过 Like、Favorite、Coin 记录互动行为
- User 1:N FavoriteFolder
- Admin 1:N AuditLog

## 6. API 设计

### 6.1 通用约定

- API 前缀：`/api`
- 请求和响应主体使用 JSON；文件上传使用 `multipart/form-data`。
- 列表接口统一支持 `page` 和 `page_size`，默认 `page=1`、`page_size=20`。
- 时间统一使用 ISO 8601 字符串。
- 需要登录的接口使用 `Authorization: Bearer <access_token>`。
- 管理端接口使用管理员 Token，和普通用户 Token 分开签发。

### 6.2 统一响应格式

成功响应：

```json
{
  "data": {},
  "message": "ok"
}
```

分页响应：

```json
{
  "data": {
    "items": [],
    "page": 1,
    "page_size": 20,
    "total": 0
  },
  "message": "ok"
}
```

错误响应：

```json
{
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "视频不存在",
    "details": {}
  }
}
```

### 6.3 用户与认证

| 方法 | 路径 | 鉴权 | 说明 |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | 否 | 用户注册 |
| POST | `/api/auth/login` | 否 | 用户登录 |
| POST | `/api/auth/refresh` | 否 | 刷新 Access Token |
| POST | `/api/auth/logout` | 是 | 退出登录 |
| GET | `/api/users/me` | 是 | 获取当前用户信息 |
| PUT | `/api/users/me` | 是 | 更新当前用户信息 |
| GET | `/api/users/{id}` | 否 | 获取指定用户公开信息 |
| GET | `/api/users/{id}/videos` | 否 | 获取用户发布的视频 |

注册请求示例：

```json
{
  "username": "dreamer",
  "email": "dreamer@example.com",
  "password": "password123"
}
```

登录响应示例：

```json
{
  "data": {
    "access_token": "jwt",
    "refresh_token": "jwt",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "dreamer",
      "avatar": null
    }
  },
  "message": "ok"
}
```

### 6.4 视频

| 方法 | 路径 | 鉴权 | 说明 |
| --- | --- | --- | --- |
| GET | `/api/videos` | 否 | 获取视频列表，支持分页、分区、排序 |
| POST | `/api/videos` | 是 | 上传视频 |
| GET | `/api/videos/{id}` | 否 | 获取视频详情 |
| PUT | `/api/videos/{id}` | 作者/管理员 | 更新视频信息 |
| DELETE | `/api/videos/{id}` | 作者/管理员 | 删除视频 |
| GET | `/api/videos/{id}/parts` | 否 | 获取分 P 列表 |
| POST | `/api/videos/{id}/view` | 否 | 记录播放 |

视频列表查询参数：

| 参数 | 说明 |
| --- | --- |
| page | 页码 |
| page_size | 每页数量 |
| category_id | 分区 ID |
| sort | `latest` / `popular` / `most_liked` |
| keyword | 标题关键词 |

上传视频使用 `multipart/form-data`：

| 字段 | 说明 |
| --- | --- |
| title | 标题 |
| description | 描述 |
| category_id | 分区 ID |
| cover | 封面文件 |
| parts | 一个或多个视频文件 |
| part_titles | 分 P 标题数组 |

### 6.5 评论与互动

| 方法 | 路径 | 鉴权 | 说明 |
| --- | --- | --- | --- |
| GET | `/api/videos/{id}/comments` | 否 | 获取视频评论 |
| POST | `/api/videos/{id}/comments` | 是 | 发表评论 |
| DELETE | `/api/comments/{id}` | 作者/管理员 | 删除评论 |
| POST | `/api/videos/{id}/like` | 是 | 点赞 |
| DELETE | `/api/videos/{id}/like` | 是 | 取消点赞 |
| POST | `/api/videos/{id}/favorite` | 是 | 收藏 |
| DELETE | `/api/videos/{id}/favorite` | 是 | 取消收藏 |
| POST | `/api/videos/{id}/coin` | 是 | 投币 |
| POST | `/api/reports` | 是 | 举报内容 |

### 6.6 内容发现

| 方法 | 路径 | 鉴权 | 说明 |
| --- | --- | --- | --- |
| GET | `/api/feed` | 否 | 首页推荐 |
| GET | `/api/search` | 否 | 搜索 |
| GET | `/api/ranking` | 否 | 排行榜 |
| GET | `/api/categories` | 否 | 获取分区列表 |
| GET | `/api/categories/{id}/videos` | 否 | 获取分区视频 |

搜索参数：

| 参数 | 说明 |
| --- | --- |
| q | 搜索关键词 |
| category_id | 分区 ID |
| sort | `relevance` / `latest` / `views` |

### 6.7 管理端

| 方法 | 路径 | 鉴权 | 说明 |
| --- | --- | --- | --- |
| POST | `/api/admin/login` | 否 | 管理员登录 |
| GET | `/api/admin/stats` | 管理员 | 数据统计 |
| GET | `/api/admin/users` | 管理员 | 用户列表 |
| PUT | `/api/admin/users/{id}/ban` | 管理员 | 封禁用户 |
| PUT | `/api/admin/users/{id}/unban` | 管理员 | 解封用户 |
| GET | `/api/admin/videos` | 管理员 | 视频列表 |
| PUT | `/api/admin/videos/{id}/status` | 管理员 | 审核或下架视频 |
| GET | `/api/admin/reports` | 管理员 | 举报列表 |
| PUT | `/api/admin/reports/{id}` | 管理员 | 处理举报 |
| GET | `/api/admin/categories` | 管理员 | 分区列表 |
| POST | `/api/admin/categories` | 管理员 | 新增分区 |
| PUT | `/api/admin/categories/{id}` | 管理员 | 更新分区 |
| DELETE | `/api/admin/categories/{id}` | 管理员 | 停用分区 |

审核请求示例：

```json
{
  "status": "published",
  "reason": ""
}
```

## 7. 前端页面设计

### 7.1 路由规划

| 路径 | 页面 | 说明 |
| --- | --- | --- |
| `/` | 首页 | 推荐视频流、分区导航、搜索入口 |
| `/video/:id` | 视频详情页 | 播放器、视频信息、互动和评论 |
| `/upload` | 投稿页 | 上传视频和填写投稿信息 |
| `/user/:id` | 用户主页 | 用户信息、投稿列表、收藏公开信息 |
| `/search` | 搜索结果页 | 视频列表和筛选条件 |
| `/ranking` | 排行榜页 | 全站和分区排行榜 |
| `/account` | 个人中心 | 个人信息、我的视频、我的收藏 |
| `/login` | 登录页 | 普通用户登录 |
| `/register` | 注册页 | 普通用户注册 |
| `/admin/login` | 管理员登录页 | 管理端入口 |
| `/admin` | 管理仪表盘 | 数据概览 |
| `/admin/users` | 用户管理页 | 用户列表和封禁 |
| `/admin/videos` | 视频审核页 | 视频审核和下架 |
| `/admin/reports` | 举报管理页 | 举报处理 |
| `/admin/categories` | 分区管理页 | 分区维护 |

### 7.2 用户端页面

#### 首页

- 顶部导航：Logo、搜索框、登录入口、投稿按钮。
- 分区导航：展示启用状态的分区。
- 推荐视频流：按发布时间、播放量和互动数综合排序，第一阶段可使用简单权重。
- 视频卡片：封面、标题、作者、播放量、发布时间。

#### 视频详情页

- 视频播放器：支持分 P 切换，显示加载、播放失败和无权限状态。
- 视频信息：标题、作者、发布时间、播放量、简介、分区。
- 互动按钮：点赞、收藏、投币、举报。
- 评论区：评论列表、回复、删除自己的评论。

#### 投稿页

- 视频文件选择和封面上传。
- 标题、简介、分区、分 P 标题。
- 上传进度和错误提示。
- 提交成功后展示审核中状态。

#### 个人中心

- 资料编辑：头像、简介。
- 我的视频：按审核状态筛选。
- 我的收藏：按收藏夹查看。

### 7.3 管理端页面

#### 仪表盘

- 用户总数、视频总数、待审核视频数、待处理举报数。
- 近期上传趋势和互动数据。

#### 用户管理页

- 用户列表：用户名、邮箱、注册时间、状态。
- 操作：封禁、解封、查看用户投稿。

#### 视频审核页

- 筛选：待审核、已发布、已拒绝、已下架。
- 审核详情：播放视频、查看标题、简介、作者和举报信息。
- 操作：通过、拒绝、下架，拒绝和下架必须填写原因。

#### 举报管理页

- 举报列表：举报人、目标类型、原因、状态。
- 操作：处理、驳回、跳转目标内容。

### 7.4 前端组件

| 组件 | 职责 |
| --- | --- |
| `VideoCard` | 视频卡片，展示封面、标题、作者和统计数据 |
| `VideoPlayer` | 视频播放器，支持分 P 切换和错误状态 |
| `CommentList` | 评论列表和回复展示 |
| `CommentEditor` | 评论输入框 |
| `UserAvatar` | 用户头像和默认头像 |
| `SearchBar` | 搜索框 |
| `CategoryNav` | 分区导航 |
| `UploadForm` | 投稿表单 |
| `AdminTable` | 管理端通用表格 |
| `StatusBadge` | 状态标签 |

### 7.5 状态管理

Pinia Store 建议拆分：

| Store | 状态 |
| --- | --- |
| `authStore` | 当前用户、Token、登录状态 |
| `videoStore` | 当前视频详情、分 P、互动状态 |
| `categoryStore` | 分区列表 |
| `adminStore` | 管理员信息和后台统计 |

## 8. 后端架构

### 8.1 项目结构

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy 模型
│   │   ├── user.py
│   │   ├── video.py
│   │   ├── comment.py
│   │   ├── interaction.py
│   │   ├── category.py
│   │   └── admin.py
│   ├── schemas/             # Pydantic 模型
│   ├── api/                 # API 路由
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── videos.py
│   │   ├── comments.py
│   │   ├── interactions.py
│   │   ├── categories.py
│   │   └── admin.py
│   ├── services/            # 业务逻辑
│   ├── utils/               # 工具函数
│   └── middleware/          # 中间件
├── alembic/                 # 数据库迁移
├── tests/                   # 测试
├── requirements.txt
└── Dockerfile
```

### 8.2 Service 划分

| Service | 职责 |
| --- | --- |
| `AuthService` | 注册、登录、Token 刷新、密码校验 |
| `UserService` | 用户资料、封禁状态检查 |
| `VideoService` | 视频创建、更新、详情、列表、状态流转 |
| `StorageService` | 文件保存、文件类型校验、URL 生成 |
| `CommentService` | 评论创建、查询、删除 |
| `InteractionService` | 点赞、收藏、投币和计数维护 |
| `AdminService` | 管理端权限、审核、举报处理 |
| `CategoryService` | 分区查询和维护 |

### 8.3 认证机制

- JWT Token 分为 Access Token 和 Refresh Token。
- Access Token 有效期：2 小时。
- Refresh Token 有效期：30 天。
- 用户 Token 和管理员 Token 使用不同的 `audience` 或 `subject` 类型区分。
- 后端依赖函数提供 `get_current_user`、`get_current_admin` 和 `require_admin_role`。

### 8.4 权限规则

| 操作 | 权限 |
| --- | --- |
| 编辑用户资料 | 当前用户本人 |
| 上传视频 | 登录且未封禁用户 |
| 修改视频信息 | 视频作者或管理员 |
| 删除视频 | 视频作者或管理员 |
| 审核视频 | 管理员 |
| 删除评论 | 评论作者或管理员 |
| 管理分区 | 管理员 |
| 管理管理员账号 | 超级管理员 |

## 9. 文件上传与存储

### 9.1 目录规划

```
storage/
├── videos/
│   └── 2026/06/25/{uuid}.mp4
├── covers/
│   └── 2026/06/25/{uuid}.jpg
└── avatars/
    └── 2026/06/25/{uuid}.jpg
```

### 9.2 文件限制

| 类型 | 允许格式 | 第一阶段大小限制 |
| --- | --- | --- |
| 视频 | mp4, webm | 单文件 500MB |
| 封面 | jpg, jpeg, png, webp | 单文件 5MB |
| 头像 | jpg, jpeg, png, webp | 单文件 2MB |

后端必须根据文件内容或 MIME 类型做校验，不能只信任文件扩展名。

### 9.3 静态访问

- Nginx 将 `/media/` 映射到后端共享的 `storage/` 目录。
- 数据库中保存相对路径，例如 `/media/videos/2026/06/25/{uuid}.mp4`。
- 第一阶段不做私有视频防盗链；如后续需要，可改为后端签名 URL。

## 10. 搜索、推荐和排行

### 10.1 搜索

第一阶段使用 PostgreSQL 基础查询：

- 标题 `ILIKE` 关键词。
- 简介 `ILIKE` 关键词。
- 仅搜索 `published` 状态视频。
- 支持分区过滤和排序。

后续可升级为 PostgreSQL Full Text Search 或 Elasticsearch。

### 10.2 推荐

第一阶段首页推荐使用规则排序：

```
score = view_count * 1 + like_count * 5 + favorite_count * 8 + coin_count * 10
```

同分时按发布时间倒序排列。为避免老视频长期霸榜，可在后续加入时间衰减。

### 10.3 排行榜

- 日榜：最近 1 天发布或产生互动的视频。
- 周榜：最近 7 天发布或产生互动的视频。
- 全站榜：不限制时间。
- 排序分数沿用推荐分数，第一阶段可直接实时计算。

## 11. 错误处理

### 11.1 常见错误码

| 错误码 | HTTP 状态 | 说明 |
| --- | --- | --- |
| `AUTH_INVALID_CREDENTIALS` | 401 | 用户名或密码错误 |
| `AUTH_TOKEN_EXPIRED` | 401 | Token 已过期 |
| `AUTH_REQUIRED` | 401 | 未登录 |
| `PERMISSION_DENIED` | 403 | 权限不足 |
| `USER_BANNED` | 403 | 用户已被封禁 |
| `VIDEO_NOT_FOUND` | 404 | 视频不存在 |
| `COMMENT_NOT_FOUND` | 404 | 评论不存在 |
| `VALIDATION_ERROR` | 422 | 参数验证失败 |
| `FILE_TOO_LARGE` | 413 | 文件过大 |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | 文件类型不支持 |
| `RATE_LIMITED` | 429 | 请求过于频繁 |

### 11.2 前端错误展示

- 表单校验错误显示在字段附近。
- API 业务错误使用页面内提示或 Toast。
- 播放失败显示播放器内错误态。
- 401 过期时尝试刷新 Token；刷新失败后跳转登录页。

## 12. 安全设计

- 密码只保存哈希，不保存明文。
- JWT Secret 必须来自环境变量。
- 上传文件名使用 UUID，不使用用户原始文件名作为存储文件名。
- 后端限制上传文件大小和类型。
- 用户输入展示时进行 HTML 转义，避免 XSS。
- 跨域只允许配置中的前端域名。
- 管理端接口必须单独鉴权。
- 对登录、注册、评论、上传等接口增加基础限流。
- 管理员操作写入 `AuditLog`。

## 13. 性能与可用性

- 视频列表接口只返回列表所需字段，详情页再获取完整信息。
- 视频卡片封面使用懒加载。
- 数据库为 `videos.status`、`videos.category_id`、`videos.created_at`、`comments.video_id` 建索引。
- 计数字段在互动写入时同步更新，避免列表页频繁聚合。
- 上传大文件时前端展示进度，后端配置合理超时。
- 第一阶段不做分片上传；如上传体验不足，后续再引入分片和断点续传。

## 14. 测试策略

### 14.1 后端测试

| 类型 | 覆盖内容 |
| --- | --- |
| 单元测试 | AuthService、VideoService、InteractionService 的业务规则 |
| API 测试 | 注册、登录、视频上传、评论、审核等接口 |
| 权限测试 | 未登录、非作者、封禁用户、管理员角色 |
| 数据约束测试 | 重复点赞、重复邮箱、非法状态流转 |

重点用例：

- 注册重复邮箱返回 `VALIDATION_ERROR`。
- 登录密码错误返回 `AUTH_INVALID_CREDENTIALS`。
- 未登录用户不能上传视频。
- 非作者不能编辑他人视频。
- 待审核视频不出现在公开视频列表。
- 同一用户重复点赞不会重复增加计数。
- 管理员审核通过后视频可在前台访问。

### 14.2 前端测试

| 类型 | 覆盖内容 |
| --- | --- |
| 单元测试 | API 封装、Store、基础组件 |
| 组件测试 | VideoCard、CommentList、UploadForm |
| 页面测试 | 登录页、视频详情页、投稿页 |

### 14.3 端到端测试

建议覆盖最小主链路：

1. 用户注册并登录。
2. 用户上传视频。
3. 管理员审核通过。
4. 游客在首页看到视频并进入详情页播放。
5. 登录用户评论、点赞、收藏、投币。

## 15. 部署设计

### 15.1 Docker Compose 配置

```yaml
services:
  frontend:
    build: ./web
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dreamlink
      - SECRET_KEY=${SECRET_KEY}
      - MEDIA_ROOT=/app/storage
    volumes:
      - media_data:/app/storage
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dreamlink
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - media_data:/var/www/media
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  media_data:
```

### 15.2 Nginx 职责

- 前端静态文件服务。
- `/api/` 反向代理到后端。
- `/media/` 映射视频、封面和头像文件。
- 配置上传大小限制。
- 配置基础缓存策略，封面可长缓存，API 不缓存。

### 15.3 环境变量

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | PostgreSQL 连接串 |
| `SECRET_KEY` | JWT 签名密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 有效期 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 有效期 |
| `MEDIA_ROOT` | 上传文件根目录 |
| `MEDIA_URL` | 静态文件 URL 前缀 |
| `CORS_ORIGINS` | 允许跨域来源 |

## 16. 项目结构

```
MIMO/
├── web/                          # 前端项目
│   ├── src/
│   │   ├── assets/               # 静态资源
│   │   ├── components/           # 通用组件
│   │   ├── views/                # 页面组件
│   │   ├── router/               # 路由配置
│   │   ├── stores/               # Pinia 状态管理
│   │   ├── api/                  # API 请求封装
│   │   ├── utils/                # 工具函数
│   │   ├── styles/               # 全局样式
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
│
├── server/                       # 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   ├── utils/
│   │   └── middleware/
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-06-25-dreamlink-design.md
│
├── docker-compose.yml
├── nginx.conf
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

## 17. 第一阶段开发计划

### 17.1 里程碑

| 阶段 | 内容 | 验收标准 |
| --- | --- | --- |
| 1 | 搭建前后端脚手架 | 前端首页可访问，后端健康检查可访问 |
| 2 | 用户系统 | 注册、登录、获取当前用户接口可用 |
| 3 | 数据模型与迁移 | 核心表可通过 Alembic 创建 |
| 4 | 视频上传与播放 | 登录用户可上传视频，公开视频可播放 |
| 5 | 评论和互动 | 评论、点赞、收藏、投币主流程可用 |
| 6 | 内容发现 | 首页、搜索、分区和排行榜可用 |
| 7 | 管理端 | 管理员可审核视频和处理举报 |
| 8 | 部署 | Docker Compose 可一键启动完整系统 |

### 17.2 最小可用版本范围

最小可用版本必须包含：

- 普通用户注册登录。
- 视频上传、审核、展示和播放。
- 首页视频列表和视频详情页。
- 评论和点赞。
- 管理员登录和视频审核。
- Docker Compose 本地启动。

可延后：

- 收藏夹多文件夹管理。
- 投币余额体系。
- 弹幕。
- 高级推荐。
- 复杂后台统计图表。

## 18. 待确认问题

以下问题会影响后续实现细节，开始编码前建议确认：

1. 视频是否必须先审核后展示，还是作者上传后可以直接发布。
2. 第一阶段是否需要真实弹幕，还是只保留播放器入口。
3. 上传视频是否需要转码；如果需要，应增加异步任务队列和转码服务。
4. 管理员账号是通过初始化脚本创建，还是由超级管理员在后台创建。
5. 是否需要移动端适配到完整可用，还是第一阶段以桌面端为主。
