# 🚀 AIGC图片生成助手 - 部署文档

## 📋 目录

- [系统要求](#系统要求)
- [快速部署](#快速部署)
- [详细部署步骤](#详细部署步骤)
- [环境配置](#环境配置)
- [生产环境部署](#生产环境部署)
- [常见问题](#常见问题)

---

## 系统要求

### 硬件要求
- CPU: 2核心以上
- 内存: 4GB以上（推荐8GB）
- 磁盘: 20GB以上可用空间

### 软件要求
- **操作系统**: Linux（推荐Ubuntu 20.04+）/ Windows 10+ / macOS
- **Python**: 3.8+ （推荐3.10或3.11）
- **Node.js**: 16+ （推荐18+）
- **数据库**: SQLite（默认）/ PostgreSQL / MySQL

### 必需的API密钥
- Google Generative AI API Key（用于图片生成）
- 阿里云OSS（用于图片存储，可选）
- OpenRouter API Key（可选，用于其他模型）

---

## 快速部署

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

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建环境变量文件
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥

# 初始化数据库和管理员账户
python init_database.py

# 启动后端服务
python start_server.py
```

### 3. 前端部署
```bash
# 打开新终端，进入项目根目录
cd ai-image

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 或生产环境构建
npm run build
```

### 4. 访问应用
- 前端地址: http://localhost:3000
- 后端API: http://localhost:5000
- 默认管理员: `admin` / `admin123`

---

## 详细部署步骤

### 步骤1: 环境准备

#### 1.1 安装Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS (使用Homebrew)
brew install python@3.10

# Windows
# 从 https://www.python.org/downloads/ 下载安装
```

#### 1.2 安装Node.js
```bash
# Ubuntu/Debian (使用NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# macOS (使用Homebrew)
brew install node

# Windows
# 从 https://nodejs.org/ 下载安装
```

### 步骤2: 后端配置

#### 2.1 创建虚拟环境
```bash
cd backend
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

#### 2.2 安装Python依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.3 配置环境变量
创建 `.env` 文件：
```bash
# Google Generative AI配置
GOOGLE_API_KEY=你的_Google_API_密钥
GOOGLE_MODEL_NAME=gemini-2.0-flash-exp

# OpenRouter配置（可选）
OPENROUTER_API_KEY=你的_OpenRouter_API_密钥

# 阿里云OSS配置（可选，用于图片存储）
OSS_ACCESS_ID=你的_OSS_Access_ID
OSS_ACCESS_KEY=你的_OSS_Access_Key
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_BUCKET=your-bucket-name
OSS_ENABLED=true

# 数据库配置
DATABASE_URL=sqlite:///aigc_assistant.db
# 或使用PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/aigc_db

# Flask配置
SECRET_KEY=your-secret-key-change-in-production-2024
FLASK_ENV=production

# 文件上传配置
MAX_CONTENT_LENGTH=52428800
UPLOAD_FOLDER=uploads

# 服务器配置
HOST=0.0.0.0
PORT=5000
```

#### 2.4 初始化数据库
```bash
# 初始化数据库表和创建管理员账户
python init_database.py

# 默认管理员账户
# 用户名: admin
# 密码: admin123
```

#### 2.5 配置OSS CORS（如果使用OSS）
```bash
python utils/oss_cors_setup.py
```

### 步骤3: 前端配置

#### 3.1 安装依赖
```bash
cd ..  # 回到项目根目录
npm install
```

#### 3.2 配置API地址
编辑 `src/config/index.js`：
```javascript
export default {
  api: {
    baseURL: process.env.NODE_ENV === 'production' 
      ? 'https://your-domain.com/api'  // 生产环境API地址
      : 'http://localhost:5000/api'    // 开发环境API地址
  }
}
```

#### 3.3 开发模式启动
```bash
npm run dev
```

#### 3.4 生产环境构建
```bash
npm run build
# 构建产物在 dist/ 目录
```

---

## 环境配置

### 数据库配置

#### SQLite（默认）
```bash
# 无需额外配置，自动创建
DATABASE_URL=sqlite:///aigc_assistant.db
```

#### PostgreSQL
```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb aigc_db
sudo -u postgres psql -c "CREATE USER aigc_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aigc_db TO aigc_user;"

# 配置环境变量
DATABASE_URL=postgresql://aigc_user:your_password@localhost/aigc_db

# 安装Python驱动
pip install psycopg2-binary
```

#### MySQL
```bash
# 安装MySQL
sudo apt install mysql-server

# 创建数据库
mysql -u root -p
CREATE DATABASE aigc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aigc_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON aigc_db.* TO 'aigc_user'@'localhost';
FLUSH PRIVILEGES;

# 配置环境变量
DATABASE_URL=mysql+pymysql://aigc_user:your_password@localhost/aigc_db

# 安装Python驱动
pip install pymysql
```

### 阿里云OSS配置

1. 登录阿里云控制台
2. 开通对象存储OSS服务
3. 创建Bucket
4. 获取AccessKey ID和AccessKey Secret
5. 配置CORS规则（运行 `python utils/oss_cors_setup.py`）

---

## 生产环境部署

### 方案1: 使用Nginx + Gunicorn

#### 1. 安装Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### 2. 配置Nginx
创建 `/etc/nginx/sites-available/aigc-assistant`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/ai-image/dist;
        try_files $uri $uri/ /index.html;
        
        # 开启gzip压缩
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }

    # 文件上传大小限制
    client_max_body_size 50M;
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/aigc-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 3. 使用Gunicorn启动后端
```bash
cd backend

# 使用Gunicorn启动
gunicorn -w 4 -b 127.0.0.1:5000 --timeout 600 'app:create_app()'

# 或使用start_server.py
python start_server.py
```

#### 4. 配置systemd服务
创建 `/etc/systemd/system/aigc-backend.service`：
```ini
[Unit]
Description=AIGC Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/ai-image/backend
Environment="PATH=/path/to/ai-image/backend/venv/bin"
ExecStart=/path/to/ai-image/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 600 'app:create_app()'
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable aigc-backend
sudo systemctl start aigc-backend
sudo systemctl status aigc-backend
```

### 方案2: 使用Docker

#### 1. 创建Dockerfile（后端）
`backend/Dockerfile`：
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "600", "app:create_app()"]
```

#### 2. 创建Dockerfile（前端）
`Dockerfile`：
```dockerfile
FROM node:18 AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

#### 3. 创建docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DATABASE_URL=postgresql://aigc:password@db:5432/aigc_db
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/instance:/app/instance
    depends_on:
      - db

  frontend:
    build: .
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=aigc_db
      - POSTGRES_USER=aigc
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 4. 启动服务
```bash
docker-compose up -d
```

### 方案3: 使用Vercel/Netlify（前端）+ Railway/Render（后端）

#### 前端部署到Vercel
```bash
npm install -g vercel
vercel login
vercel
```

#### 后端部署到Railway
1. 访问 https://railway.app
2. 连接GitHub仓库
3. 选择backend目录
4. 配置环境变量
5. 自动部署

---

## HTTPS配置（使用Let's Encrypt）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 性能优化

### 1. 启用Redis缓存
```bash
# 安装Redis
sudo apt install redis-server

# Python中使用
pip install redis
```

### 2. 配置CDN
- 将静态资源上传到OSS
- 启用OSS的CDN加速
- 配置前端资源使用CDN地址

### 3. 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_user_id ON generation_tasks(user_id);
CREATE INDEX idx_created_at ON generation_history(created_at);
```

---

## 监控和日志

### 1. 配置日志
编辑 `backend/app.py`：
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 使用PM2监控Node.js应用
```bash
npm install -g pm2
pm2 start npm --name "aigc-frontend" -- run dev
pm2 startup
pm2 save
```

---

## 常见问题

### Q1: 端口被占用
```bash
# Linux/macOS
sudo lsof -i :5000
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Q2: 数据库连接失败
- 检查DATABASE_URL配置
- 确认数据库服务已启动
- 验证用户权限

### Q3: API密钥无效
- 确认 `.env` 文件存在
- 检查API密钥格式
- 验证API配额

### Q4: 图片上传失败
- 检查`MAX_CONTENT_LENGTH`配置
- 确认`uploads`目录权限
- 验证OSS配置（如果使用）

### Q5: 前端无法连接后端
- 检查`src/config/index.js`中的`baseURL`
- 确认后端服务已启动
- 检查CORS配置

---

## 安全建议

1. **修改默认密码**: 首次登录后立即修改admin密码
2. **使用HTTPS**: 生产环境必须使用HTTPS
3. **定期备份**: 定期备份数据库和上传的文件
4. **限制访问**: 使用防火墙限制不必要的端口
5. **更新依赖**: 定期更新Python和npm依赖包
6. **环境变量**: 不要将`.env`文件提交到版本控制

---

## 备份和恢复

### 备份SQLite数据库
```bash
cp backend/instance/aigc_assistant.db backup/aigc_assistant_$(date +%Y%m%d).db
```

### 备份PostgreSQL
```bash
pg_dump -U aigc_user aigc_db > backup/aigc_db_$(date +%Y%m%d).sql
```

### 恢复数据库
```bash
# SQLite
cp backup/aigc_assistant_20240101.db backend/instance/aigc_assistant.db

# PostgreSQL
psql -U aigc_user aigc_db < backup/aigc_db_20240101.sql
```

---

## 联系和支持

- 文档: [docs/README.md](docs/README.md)
- Issues: GitHub Issues
- Email: support@example.com

---

**祝部署顺利！🎉**

