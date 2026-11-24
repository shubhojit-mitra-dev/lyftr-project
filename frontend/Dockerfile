# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for React + TypeScript Vite Frontend

# ==========================================
# Stage 1: Build Frontend Assets
# ==========================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests for deterministic layer caching
COPY package.json package-lock.json ./

# Clean installation of dependencies
RUN npm ci

# Copy project source code and configs
COPY . ./

# Allow build-time configuration of VITE_API_URL (defaults to empty so runtime falls back to http://localhost:8000)
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL

# Build production bundle with TypeScript check and Vite
RUN npm run build

# ==========================================
# Stage 2: Production Nginx Runtime
# ==========================================
FROM nginx:alpine AS runtime

# Remove default nginx static assets and configuration
RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration with SPA routing and port 3000 listener
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static distribution from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
