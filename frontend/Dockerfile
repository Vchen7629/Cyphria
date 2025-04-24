# build stage
FROM node:23-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci --include=dev

COPY . .

RUN npm run build

#Server
FROM node:23-alpine

WORKDIR /app

COPY --from=build /app/dist ./build

RUN npm install