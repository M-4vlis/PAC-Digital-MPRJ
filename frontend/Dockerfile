FROM node:22-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY vendor ./vendor
COPY types ./types
RUN npm install --global pnpm@10.18.3 && pnpm install --frozen-lockfile
COPY index.html tsconfig.json tsconfig.node.json vite.config.ts ./
COPY src ./src
RUN pnpm build

FROM nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
