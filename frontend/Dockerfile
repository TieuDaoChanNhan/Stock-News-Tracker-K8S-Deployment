# Base image
FROM nginx:alpine

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy Flutter build output (chỉ cần build/web)
COPY build /usr/share/nginx/html

# Copy custom nginx config
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
