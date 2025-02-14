FROM node:22

WORKDIR /app

COPY package*.json ./
RUN npm install --optional=true

COPY . .

RUN npm run build

# Node sucks so it needs -- before --host
CMD ["npm", "run", "preview", "--", "--host"]