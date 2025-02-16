FROM node:22-alpine

COPY package*.json ./

RUN npm ci --include=dev

#build stage

FROM node:22-alpine

WORKDIR /app

COPY --from=cache ./node_modules ./node_modules

COPY . .

RUN npm install && npm run build

