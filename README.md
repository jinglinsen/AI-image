# 🎨 AIGC图片生成助手 V3.0

基于AI的专业级电商产品图片生成工具，支持多种图片类型生成、用户认证、历史记录管理等完整功能。

---

## ✨ 功能特性

### 🎯 核心功能

#### 1. 智能图片生成
- **7种图片类型**: 主图、尺寸图、细节图、场景图、多角度图、互动图、多样性图
- **AI模型支持**: Google Gemini 2.0、Nano Banana等多种模型
- **流式生成**: 实时进度反馈，即时查看生成结果
- **参考图支持**: 支持产品图、竞品图、参考图等多种图片类型
- **图片再创作**: 基于已生成图片进行迭代优化

#### 2. 用户系统
- **注册登录**: 手机号/邮箱注册，支持邀请码机制
- **权限管理**: 管理员和普通用户两种角色
- **密码修改**: 用户可自行修改密码
- **会话保持**: 15天免登录（使用Cookie）

#### 3. 管理后台
- **用户管理**: 查看用户列表、重置密码、删除用户
- **使用统计**: 查看用户的生成次数、图片数量
- **邀请码管理**: 生成、查看、删除邀请码，支持批量操作
- **分页显示**: 邀请码列表支持20/50/100条每页

#### 4. 历史记录
- **自动保存**: 生成前后自动保存任务参数和结果
- **实时同步**: 删除图片后自动更新历史记录
- **标题管理**: 自动使用产品标题，支持重命名
- **置顶功能**: 重要任务可置顶显示
- **参数恢复**: 点击历史记录恢复所有任务参数

#### 5. 图片管理
- **多种上传方式**: 拖拽、点击、粘贴、URL
- **OSS存储**: 支持阿里云OSS云存储
- **本地存储**: 支持本地文件系统存储
- **图片预览**: 大图预览、下载、删除等操作

---

## 🎨 界面设计

### 三栏式工作台布局

**左栏 - 输入配置区**
- 产品信息（标题、卖点、尺寸）
- 产品图片上传
- 参考图片管理
- 竞品分析
- 可收起设计

**中栏 - 主创作区**
- AI模型选择
- 图片类型选择
- 主提示词输入
- 生成结果展示
- 图片操作（下载、删除、再创作）

**右栏 - 资源管理区**
- 历史记录列表
- 历史记录操作（置顶、重命名、删除）
- 用户信息
- 退出登录

---

## 🚀 快速开始

### 环境要求
- Node.js 16+
- Python 3.8+
- SQLite / PostgreSQL / MySQL

### 1. 克隆项目
```bash
git clone <repository-url>
cd ai-image
```

### 2. 后端部署
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建.env文件，参考后续配置说明）
cp .env.example .env
# 编辑.env文件，填入你的API密钥

# 初始化数据库
python init_database.py

# 启动后端
python start_server.py
```

后端将在 `http://localhost:5000` 启动

### 3. 前端部署
```bash
# 回到项目根目录
cd ..

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 或生产环境构建
npm run build
```

前端将在 `http://localhost:3000` 启动

### 4. 默认账户
- **管理员账户**: `admin` / `admin123`
- **首次登录后请立即修改密码**

---

## ⚙️ 环境配置

### 后端环境变量 (.env)

```bash
# Google Generative AI配置（必需）
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL_NAME=gemini-2.0-flash-exp

# 阿里云OSS配置（可选）
OSS_ACCESS_ID=your_oss_access_id
OSS_ACCESS_KEY=your_oss_access_key
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_BUCKET=your-bucket-name
OSS_ENABLED=true

# 数据库配置
DATABASE_URL=sqlite:///aigc_assistant.db

# Flask配置
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# 服务器配置
HOST=0.0.0.0
PORT=5000
```

### 前端配置

编辑 `src/config/index.js`:
```javascript
export default {
  api: {
    baseURL: 'http://localhost:5000/api'
  }
}
```

---

## 📁 项目结构

```
ai-image/
├── backend/                    # 后端代码
│   ├── app.py                 # Flask主应用
│   ├── config.py              # 配置文件
│   ├── requirements.txt       # Python依赖
│   ├── init_database.py       # 数据库初始化
│   ├── start_server.py        # 启动脚本
│   ├── models/                # 数据模型
│   │   └── database.py
│   ├── services/              # 业务逻辑
│   │   ├── user_service.py
│   │   ├── invite_service.py
│   │   ├── prompt_builder.py
│   │   └── gemini_image_generator.py
│   ├── utils/                 # 工具函数
│   │   ├── auth.py
│   │   ├── image_processor.py
│   │   └── oss_uploader.py
│   └── instance/              # 实例文件（数据库、上传文件）
├── src/                       # 前端代码
│   ├── views/                 # 页面组件
│   │   ├── Login.vue
│   │   ├── AdminPanel.vue
│   │   └── AIGCWorkbench.vue
│   ├── services/              # API服务
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── adminService.js
│   │   └── aigcService.js
│   ├── components/            # 通用组件
│   └── config/                # 配置文件
├── docs/                      # 文档目录
│   ├── 历史记录功能完善总结.md
│   ├── 快速测试清单.md
│   └── ...更多文档
├── DEPLOYMENT.md              # 部署文档
├── package.json               # 前端依赖
└── vite.config.js            # Vite配置
```

---

## 🔧 核心技术栈

### 后端
- **Web框架**: Flask 2.3.3
- **ORM**: Flask-SQLAlchemy 3.0.5
- **认证**: PyJWT 2.8.0
- **图片处理**: Pillow 10.0.1
- **AI模型**: Google Generative AI 0.8.5
- **云存储**: OSS2 2.18.4
- **WSGI服务器**: Gunicorn 21.2.0

### 前端
- **框架**: Vue 3
- **构建工具**: Vite 5
- **UI库**: Element Plus
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图标**: Element Plus Icons

---

## 📚 使用指南

### 1. 用户注册和登录
1. 访问 http://localhost:3000
2. 点击"注册账号"
3. 填写用户名、密码、邮箱、邀请码
4. 注册成功后自动登录

### 2. 图片生成流程
1. **填写产品信息**: 产品标题、卖点、尺寸
2. **上传产品图片**: 支持多张图片上传
3. **添加参考图片**: 可选，用于指导AI生成
4. **选择图片类型**: 主图、细节图、场景图等
5. **输入提示词**: 可选，留空将使用默认最佳实践
6. **点击生成**: 等待AI生成图片
7. **查看结果**: 实时查看生成进度和结果

### 3. 历史记录管理
1. 点击右侧"历史记录"标签
2. 查看所有历史任务
3. 点击任意记录恢复任务参数
4. 使用"更多"按钮进行置顶/重命名/删除操作

### 4. 管理后台使用
1. 使用管理员账户登录
2. 访问 http://localhost:3000/admin
3. 管理用户、查看统计、生成邀请码

---

## 🔐 安全建议

1. ✅ **修改默认密码**: 首次登录后立即修改
2. ✅ **使用HTTPS**: 生产环境必须启用
3. ✅ **保护API密钥**: 不要将.env文件提交到版本控制
4. ✅ **定期备份**: 定期备份数据库和上传文件
5. ✅ **更新依赖**: 定期检查并更新依赖包

---

## 📖 详细文档

- [部署文档](DEPLOYMENT.md) - 完整的生产环境部署指南
- [用户认证指南](docs/USER_AUTH_GUIDE.md) - 用户系统使用说明
- [快速测试清单](docs/快速测试清单.md) - 功能测试步骤
- [历史记录功能](docs/历史记录功能完善总结.md) - 历史记录详细说明
- [更多文档](docs/) - 其他技术文档

---

## 🐛 常见问题

### Q1: 后端启动失败
```bash
# 检查依赖是否完整安装
pip install -r requirements.txt

# 检查端口是否被占用
# Linux/macOS: lsof -i :5000
# Windows: netstat -ano | findstr :5000
```

### Q2: 前端无法连接后端
- 检查 `src/config/index.js` 中的 `baseURL`
- 确认后端服务已启动
- 检查浏览器Console是否有CORS错误

### Q3: 图片上传失败
- 检查 `MAX_CONTENT_LENGTH` 配置（默认50MB）
- 确认 `backend/uploads` 目录存在且有写权限
- 如果使用OSS，检查OSS配置是否正确

### Q4: 数据库错误
```bash
# 删除旧数据库重新初始化
rm backend/instance/aigc_assistant.db
python backend/init_database.py
```

---

## 📝 版本更新

### V3.0 (当前版本)
- ✅ 完整的用户认证系统
- ✅ 管理后台和邀请码机制
- ✅ 历史记录自动保存和管理
- ✅ OSS云存储支持
- ✅ 图片再创作功能
- ✅ 流式生成和实时进度
- ✅ 深色主题专业UI

### V2.0
- ✅ 三栏式单页工作台
- ✅ 品类通用化设计
- ✅ 图片类型扩展

### V1.0
- ✅ 基础图片生成功能
- ✅ 简单的产品信息输入

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- Email: jlinnice@163.com

---

**享受AI创作的乐趣！** 🎉
