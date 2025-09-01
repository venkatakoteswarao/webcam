# =========================
# Base image
# =========================
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y openjdk-21-jdk python3.11 python3-pip maven nginx curl && \
    apt-get clean

# =========================
# Set working directory
# =========================
WORKDIR /app

# =========================
# Copy and build Spring Boot
# =========================
COPY demo/pom.xml ./demo/
COPY demo/src ./demo/src/
WORKDIR /app/demo
RUN mvn clean package -DskipTests

# =========================
# Copy Flask app
# =========================
COPY customer-churn/ /app/customer-churn
WORKDIR /app/customer-churn
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# Copy Nginx config
# =========================
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# =========================
# Expose ports
# =========================
EXPOSE 80

# =========================
# Start all services
# =========================
CMD bash -c "\
    # Start Flask API in background \
    python3 /app/customer-churn/churn.py & \
    # Start Spring Boot in background \
    java -jar /app/demo/target/*.jar & \
    # Start Nginx in foreground \
    nginx -g 'daemon off;' \
"
