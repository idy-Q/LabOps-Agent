# ==============================================================================
# LabOps-Agent 前端服务多阶段生产镜像构建 (Vue 3 + Vite + Tailwind + Nginx)
# 采用 Multi-stage 构建：
# Stage 1 (Builder): 基于 Node.js 20 编译压缩前端工程输出至 dist
# Stage 2 (Runner):  基于极轻量 nginx:alpine 托管静态资源并反向代理 API/SSE
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: 编译打包构建环境
# ------------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# 优先安装依赖，利用 Docker 构建缓存加速
COPY package*.json ./
RUN npm install

# 复制工程源码并执行 Vite 生产打包构建
COPY . .
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: 极轻量生产运行镜像 (< 30MB)
# ------------------------------------------------------------------------------
FROM nginx:alpine

# 拷贝 Stage 1 生成的高性能生产静态产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 拷贝 Nginx 规则文件 (支持 SPA 客户端路由与 API/SSE 转发)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露 HTTP 统一入口端口
EXPOSE 80

# 轻量健康检查机制
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1/ || exit 1

# 启动 Nginx 前台守护进程
CMD ["nginx", "-g", "daemon off;"]
