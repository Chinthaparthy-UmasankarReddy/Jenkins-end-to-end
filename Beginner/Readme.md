
---

# Cloud-Native End-to-End CI/CD Pipeline: Jenkins, SonarQube, Trivy, and Docker on Kubernetes

This repository provides a complete, production-ready local CI/CD pipeline setup running on **Kubernetes (Docker Desktop)**. It orchestrates ephemeral multi-container build agents to compile code, perform static analysis with SonarQube, scan container images with Trivy, and publish images to Docker Hub.

---

## 🏗️ Architecture Overview

* **Orchestration:** Local Docker Desktop Kubernetes cluster.
* **CI/CD Engine:** Jenkins Master deployed via Helm, using dynamic multi-container pods (`maven`, `trivy`, `docker`) as ephemeral agents.
* **Code Quality Gate:** SonarQube server deployed locally with a PersistentVolumeClaim (PVC) for data retention.
* **Security & Containerization:** Trivy vulnerability scanner and local Docker socket sharing (`/var/run/docker.sock`).

---

## 🛠️ Step 1: Deploy SonarQube Server on Kubernetes

SonarQube analyzes your source code for bugs, code smells, and security vulnerabilities. To prevent data loss on pod restarts, we deploy it with persistent storage.

1. Create a dedicated namespace:
```bash
kubectl create namespace sonarqube

```


2. Create a file named `sonarqube.yaml` with the following configuration:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sonarqube-data-pvc
  namespace: sonarqube
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sonarqube
  namespace: sonarqube
spec:
  selector:
    matchLabels:
      app: sonarqube
  template:
    metadata:
      labels:
        app: sonarqube
    spec:
      containers:
      - name: sonarqube
        image: sonarqube:community
        ports:
        - containerPort: 9000
          name: http
        resources:
          limits:
            memory: "3Gi"
            cpu: "1500m"
          requests:
            memory: "2Gi"
            cpu: "500m"
        volumeMounts:
        - mountPath: /opt/sonarqube/data
          name: sonarqube-data
        - mountPath: /opt/sonarqube/extensions
          name: sonarqube-extensions
        - mountPath: /opt/sonarqube/conf
          name: sonarqube-conf
        env:
        - name: SONAR_SEARCH_JAVAADDITIONALOPTS
          value: "-Dnode.store.allow_mmap=false"
      volumes:
      - name: sonarqube-data
        persistentVolumeClaim:
          claimName: sonarqube-data-pvc
      - name: sonarqube-extensions
        emptyDir: {}
      - name: sonarqube-conf
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: sonarqube-service
  namespace: sonarqube
spec:
  type: NodePort
  ports:
  - port: 9000
    targetPort: 9000
    nodePort: 30900
  selector:
    app: sonarqube

```


3. Apply the deployment manifest:
```bash
kubectl apply -f sonarqube.yaml -n sonarqube

```


4. Access SonarQube at `http://localhost:30900` (Default login: `admin` / `admin`).
5. Generate a User Token (`My Account -> Security -> Generate Token`) and save it.

(Choose Option 1 or Option 2):
Option 1: Allow Project Creation for Anyone (Easiest for Local Testing)
Open your SonarQube dashboard (http://localhost:30900) and log in as admin.

Go to Administration (top menu) -> Security -> Global Permissions.

Look for "Create Projects".

Check the box to grant this permission to Anyized Users or your specific user/group.

Save settings, then re-run your Jenkins pipeline.

Option 2: Pre-Create the Project in SonarQube
If you prefer not to change global permissions, create the project manually first:

Log into SonarQube (http://localhost:30900).

Click Create Project -> Manually.

Set:

Project key: my-java-app (must match your Maven artifactId)

Display name: my-java-app

Click Set Up, choose Local, and use your generated user token.

Once the project container/shell exists in SonarQube, your pipeline token will be fully authorized to push analysis reports to it!

---

## ⚙️ Step 2: Jenkins Credentials Setup

In your Jenkins dashboard (`http://localhost:8080`), go to **Manage Jenkins -> Credentials -> System -> Global credentials** and add:

1. **SonarQube Token:**
* **Kind:** `Secret text`
* **ID:** `sonarqube-token`
* **Secret:** Your generated SonarQube token.


2. **Docker Hub Credentials:**
* **Kind:** `Username with password`
* **ID:** `docker-hub-creds`
* **Username/Password:** Your Docker Hub credentials or Access Token.



---

## 📁 Step 3: Application Code Configurations

Ensure your repository has the following file structure:

### 1. `pom.xml`

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-java-app</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
</project>

```

### 2. `Dockerfile`

```dockerfile
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY target/my-java-app-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]

```

### 3. `src/main/java/com/example/App.java`

```java
package com.example;

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;

public class App {
    public static void main(String[] args) throws IOException {
        int port = 8080;
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
        server.createContext("/", new RootHandler());
        server.setExecutor(null);
        server.start();
        System.out.println("Server started on port " + port);
    }

    static class RootHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String response = "Hello from Cloud-Native Jenkins Pipeline!";
            exchange.sendResponseHeaders(200, response.getBytes().length);
            OutputStream os = exchange.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
    }
}

```

---

## 🚀 Step 4: The Complete `Jenkinsfile`

Place this pipeline script in the root of your repository. It runs inside a dynamic multi-container Kubernetes pod (`ci-pod`) sharing the local Docker daemon socket:

```groovy
pipeline {
    agent {
        label 'ci-pod'
    }
    
    environment {
        DOCKER_IMAGE = 'your-dockerhub-username/my-java-app'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        SONARQUBE_SERVER = 'http://sonarqube-service.sonarqube.svc.cluster.local:9000'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('2. Build & Unit Test') {
            steps {
                container('maven') {
                    sh 'mvn clean package -DskipTests=false'
                }
            }
        }

        stage('3. SonarQube Quality Gate') {
            steps {
                container('maven') {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        sh """
                            mvn org.sonarsource.scanner.maven:sonar-maven-plugin:sonar \
                            -Dsonar.host.url=${SONARQUBE_SERVER} \
                            -Dsonar.token=${SONAR_TOKEN}
                        """
                    }
                }
            }
        }

        stage('4. Build Docker Image') {
            steps {
                container('docker') {
                    sh "docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        stage('5. Trivy Container Vulnerability Scan') {
            steps {
                container('trivy') {
                    sh "trivy image --severity HIGH,CRITICAL --exit-code 1 ${DOCKER_IMAGE}:${IMAGE_TAG}"
                }
            }
        }

        stage('6. Push to Docker Hub') {
            steps {
                container('docker') {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin"
                        sh "docker push ${DOCKER_IMAGE}:${IMAGE_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }
    }

    post {
        always {
            container('maven') {
                sh 'chmod -R 777 . || true'
            }
            deleteDir()
            echo "Pipeline finished. Ephemeral agent pod destroyed cleanly."
        }
    }
}

```