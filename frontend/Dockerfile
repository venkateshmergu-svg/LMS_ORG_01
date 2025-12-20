# ============================================================
# LMS FRONTEND PRODUCTION DOCKERFILE
# ============================================================
# Multi-stage build for minimal production image
# Uses nginx for static file serving
# ============================================================

# Stage 1: Build
FROM node:20.18.0-alpine AS builder

WORKDIR /app

# Copy package files first for layer caching
COPY package.json package-lock.json ./

# Install dependencies (clean install for reproducibility)
RUN npm ci --prefer-offline

# Copy source code
COPY . .

# Build arguments for version injection
ARG VITE_BUILD_VERSION=0.0.0
ARG VITE_BUILD_COMMIT=unknown
ARG VITE_BUILD_DATE=unknown
ARG VITE_BUILD_NUMBER=0

# Set environment variables for build
ENV VITE_BUILD_VERSION=$VITE_BUILD_VERSION
ENV VITE_BUILD_COMMIT=$VITE_BUILD_COMMIT
ENV VITE_BUILD_DATE=$VITE_BUILD_DATE
ENV VITE_BUILD_NUMBER=$VITE_BUILD_NUMBER

# Build application
RUN npm run build:only

# Stage 2: Production
FROM nginx:1.25-alpine AS production

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Add labels for traceability
ARG VITE_BUILD_VERSION=0.0.0
ARG VITE_BUILD_COMMIT=unknown
ARG VITE_BUILD_DATE=unknown

LABEL org.opencontainers.image.title="LMS Frontend" \
      org.opencontainers.image.description="Leave Management System Frontend" \
      org.opencontainers.image.version="${VITE_BUILD_VERSION}" \
      org.opencontainers.image.revision="${VITE_BUILD_COMMIT}" \
      org.opencontainers.image.created="${VITE_BUILD_DATE}" \
      org.opencontainers.image.vendor="LMS Organization" \
      org.opencontainers.image.source="https://github.com/org/lms-frontend"

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/build-manifest.json || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
