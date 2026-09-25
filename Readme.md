
---

# Local Cloud-Native CI/CD: Jenkins on Kubernetes (Docker Desktop)

This repository demonstrates an industry best-practice setup for running a **Jenkins Master** inside a local Kubernetes cluster (via Docker Desktop) with **dynamic Kubernetes pods acting as build agents**.

---

## Architecture Overview

* **Master Server:** Deployed inside a local Kubernetes cluster using Helm with persistent storage.
* **Build Agents:** Ephemeral, on-demand Kubernetes pods spawned dynamically per build pipeline and terminated immediately after execution.
* **Environment:** Local Docker Desktop running a Kubernetes cluster.

---

## Prerequisites

Ensure you have the following tools installed on your machine:

* [Docker Desktop](https://www.docker.com/?utm_source=gemini) (with Kubernetes enabled in settings)
* `kubectl` CLI
* `helm` (Helm CLI package manager)

---

## Step-by-Step Setup Guide

### Step 1: Verify Kubernetes Cluster Connection

Ensure your `kubectl` context points to Docker Desktop:

```bash
kubectl config use-context docker-desktop
kubectl get nodes

```

*(You should see a single node named `docker-desktop` in the `Ready` state).*

---

### Step 2: Deploy Jenkins Master via Helm

1. Create a dedicated namespace for your CI/CD tools:
```bash
kubectl create namespace jenkins

```


2. Add and update the official Jenkins Helm repository:
```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update

```


3. Install Jenkins with persistence enabled and a custom admin password (`admin123`):
```bash
helm install jenkins jenkins/jenkins \
  --namespace jenkins \
  --set persistence.enabled=true \
  --set persistence.size=8Gi \
  --set controller.serviceType=NodePort \
  --set controller.admin.password=admin123

```



---

### Step 3: Access the Jenkins Dashboard

1. Set up local port forwarding to access the Jenkins UI:
```bash
kubectl --namespace jenkins port-forward svc/jenkins 8080:8080

```


2. Open your browser and navigate to: `http://localhost:8080`
3. Log in using:
* **Username:** `admin`
* **Password:** `admin123`


4. Complete the setup wizard (install suggested plugins and finish instance configuration).

---

### Step 4: Configure the Kubernetes Cloud Plugin

1. Go to **Manage Jenkins** -> **Plugins** -> **Available plugins** and install the **Kubernetes CLI** plugin.
2. Navigate to **Manage Jenkins** -> **Clouds** -> **New cloud**:
* **Name:** `kubernetes`
* **Type:** `Kubernetes`


3. Configure the cloud settings:
* **Kubernetes URL:** `[https://kubernetes.docker.internal:6443](https://kubernetes.docker.internal:6443)`
* **Kubernetes Namespace:** `jenkins`
* **Jenkins URL:** `[http://jenkins.jenkins.svc.cluster.local:8080](http://jenkins.jenkins.svc.cluster.local:8080)`



---

### Step 5: Configure the Pod Template (Agent Blueprint)

Scroll down to the **Pod Templates** section inside your Kubernetes cloud configuration and add a new template:

* **Name:** `maven-agent`
* **Namespace:** `jenkins`
* **Labels:** `maven`

Add a tool container to the template:

* **Name:** `maven`
* **Docker Image:** `maven:3.9-eclipse-temurin-17`
* **Command:** `sleep`
* **Arguments:** `99d`
* **Working Directory:** `/home/jenkins/agent`

---

### Step 6: Create and Run the CI/CD Pipeline Job

1. In Jenkins, create a new **Pipeline** job named `Test`.
2. Paste the following declarative `Jenkinsfile` script into the pipeline definition:

```groovy
pipeline {
    agent {
        label 'maven'
    }
    stages {
        stage('Test Pod Execution') {
            steps {
                container('maven') {
                    sh 'echo "Running inside the Maven container!"'
                    sh 'java -version'
                    sh 'mvn --version'
                }
            }
        }
    }
}

```

3. Click **Build Now**.

Jenkins will dynamically provision an isolated Kubernetes pod containing your tool container, execute the build steps cleanly, and automatically destroy the pod upon completion!