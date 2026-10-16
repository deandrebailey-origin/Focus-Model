FROM node:22-alpine AS build

# Stage 1: Build the React app

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ci install exactly what in package-lock.json

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

# Stage 2 starts fresh from nginx a fast web server
# Everythig from stage 1 is gone, we only copy the build output

COPY nginx.conf /etc.nginx.conf.d/default.conf

#replace nfinx default site config with mine

COPY --from=build /app/dist /usr/share/nginx/html

# --from build copie from stage 1 instead of from mac
# grabs dist folder and put it where nginx serves

EXPOSE 80


