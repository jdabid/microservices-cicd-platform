FROM node:20-alpine AS builder

LABEL maintainer="David Castro <david@example.com>"
LABEL description="Frontend Builder Stage"

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM nginx:1.25-alpine AS runtime

LABEL maintainer="David Castro <david@example.com>"
LABEL description="Frontend Production Image"
LABEL version="0.2.0"

COPY nginx.conf /etc/nginx/nginx.conf

COPY --from=builder /app/dist /usr/share/nginx/html

RUN addgroup -g 1000 nginxuser && \
    adduser -D -u 1000 -G nginxuser nginxuser && \
    chown -R nginxuser:nginxuser /usr/share/nginx/html && \
    chown -R nginxuser:nginxuser /var/cache/nginx && \
    chown -R nginxuser:nginxuser /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginxuser:nginxuser /var/run/nginx.pid

USER nginxuser

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]