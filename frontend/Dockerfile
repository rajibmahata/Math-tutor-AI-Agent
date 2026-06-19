FROM node:22-alpine AS base

WORKDIR /app

# =========================================================================
# Development Stage
# =========================================================================
FROM base AS development

COPY package*.json ./
RUN npm install

CMD ["npm", "run", "dev"]

# =========================================================================
# Production Build Stage
# =========================================================================
FROM base AS builder

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# =========================================================================
# Production Runtime Stage
# =========================================================================
FROM node:22-alpine AS production

WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
