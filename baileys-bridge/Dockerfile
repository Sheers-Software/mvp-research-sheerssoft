FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --omit=dev || npm install --production

# Copy source and build
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

# Create sessions directory
RUN mkdir -p /sessions

ENV NODE_ENV=production
EXPOSE 3001

CMD ["node", "dist/index.js"]
