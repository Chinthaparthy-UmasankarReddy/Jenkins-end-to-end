FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY target/my-java-app-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]