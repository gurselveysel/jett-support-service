FROM node:20-bookworm-slim
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev
COPY server.js ./
COPY data ./data
ENV NODE_ENV=production
EXPOSE 8080
CMD ["node","server.js"]