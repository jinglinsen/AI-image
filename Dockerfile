# ============================================
# AIGC 图片生成助手 - 前端构建 Dockerfile
# 多阶段构建：Node 构建 → Nginx 托管
# ============================================

# --- 阶段1：构建前端 ---
FROM node:18-alpine AS builder

WORKDIR /app

# 复制包管理文件并安装依赖
COPY package.json package-lock.json ./
RUN npm ci --registry=https://registry.npmmirror.com

# 复制源代码并构建
COPY index.html vite.config.js ./
COPY src/ src/

RUN npm run build

# --- 阶段2：Nginx 托管 ---
FROM nginx:1.25-alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置
COPY deploy/nginx.conf /etc/nginx/nginx.conf
COPY deploy/default.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/api/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
