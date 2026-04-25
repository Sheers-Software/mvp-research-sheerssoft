FROM node:20-alpine

# Baileys and its dependencies need git + build tools
RUN apk add --no-cache git python3 make g++

WORKDIR /app

# Copy manifests and install ALL deps (including devDeps needed for tsc)
COPY package.json ./
RUN npm install

# Build TypeScript
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

# Prune devDependencies for leaner production image
RUN npm prune --production

# Persistent session storage
RUN mkdir -p /sessions

ENV NODE_ENV=production
EXPOSE 3001

CMD ["node", "dist/index.js"]
