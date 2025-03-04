FROM node:22

WORKDIR /app

COPY package*.json ./
RUN npm install --optional=true

COPY . .


# FOR DEVELOPMENT
# Node sucks so it needs -- before --host
CMD ["npm", "run", "dev", "--", "--host"]

# FOR PRODUCTION
# RUN npm run build

# Node sucks so it needs -- before --host
# CMD ["npm", "run", "preview", "--", "--host"]