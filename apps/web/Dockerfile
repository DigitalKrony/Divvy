FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

ENV PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright
RUN npx playwright install chromium

COPY . .

EXPOSE 5173 6006