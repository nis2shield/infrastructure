# React NIS2 Guard Demo Frontend
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install serve for production
RUN npm install -g serve

# Copy built files
COPY --from=builder /app/dist ./dist

# Non-root user
RUN adduser -D appuser
USER appuser

EXPOSE 5173

CMD ["serve", "-s", "dist", "-l", "5173"]
