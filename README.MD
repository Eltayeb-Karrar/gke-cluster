# Comprehensive Assessment Project

This project aim to develop and deploy Google Kubernetes Engine (GKE) with different sample applications(Service). It includes the application source code, infrastructure as code (IaC) for provisioning the cloud resources, and Kubernetes configurations for deploying the application and its dependencies.

## Architecture

The architecture consists of the following components:

- **Applications**: 3 microservices (`api-service`, `iam-service`, `image-service`) and a MongoDB database. (API Docs Included)
- **Infrastructure**: A GKE cluster, VPC, subnetwork, NAT, and a GCS bucket on Google Cloud Platform (GCP).
- **Cluster Components**:
    - **nginx-ingress**: For managing external access to the services in the cluster.
    - **cert-manager**: For automating the management of TLS certificates.
    - **external-secrets**: For managing secrets from external secret stores like GCP Secret Manager.
    - **prometheus-operator**: For monitoring the cluster and applications.
    - **loki & promtail**: For log aggregation and collection.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

- `gcloud` CLI
- `kubectl`
- `terraform`
- `helm`
- Docker
- A GCP project with billing enabled
- A domain name managed through Cloudflare

You will also need a GCP service account key file named `thm-assess-sa.json` in the root directory of this project.

## Deployment Steps

Follow these steps to deploy the entire application stack:

### 1. Provision the Infrastructure

This step uses Terraform to create the necessary GCP resources.

```bash
cd "2 provision infrastructure"
terraform init
terraform plan
terraform apply
```

### 2. Install Cluster Components

This step uses Helm to install the core components in the GKE cluster.

```bash
cd "3 cluster-components"
helm upgrade --install ingress-nginx ./nginx-ingress-wrapper/ -n ingress-nginx --create-namespace
helm upgrade --install cert-manager ./cert-manager-wrapper/ -n cert-manager --create-namespace
helm upgrade --install secret-operator ./external-secrets-wrapper/ -n secret-operator --create-namespace
helm upgrade --install kube-prom-stack ./prometheus-operator-wrapper/ -n observability --create-namespace
helm upgrade --install loki ./loki-wrapper/ -n loki --create-namespace
helm upgrade --install promtail ./log-collector-wrapper/ -n promtail --create-namespace
```

### 3. Configure the Cluster

This step configures `cert-manager` and `external-secrets`.

**Note:** Make sure you have a secret in GCP Secret Manager for the Cloudflare API token.

```bash
cd "4 Kubernetes Configuration"
# Create a secret for the GCP service account
kubectl create secret generic gcp-sa-key --from-file=secret-key.json=./thm-assess-sa.json --namespace=cert-manager

# Apply the configurations
kubectl apply -f ./SecretOperatorConfig/
kubectl apply -f ./CertManagerConfig/
```

### 4. Deploy the Applications

This step deploys the microservices and MongoDB using Kustomize.

**Note:** You need to place a copy of the `thm-assess-sa.json` file as `secret-key.json` in the `5 Application Configuration/_Components/SharedSecrets/` directory.

```bash
cd "5 Application Configuration"
kubectl apply -k .
```

## Local Development

You can run the applications locally using Docker Compose.

```bash
cd "1 applications"
docker compose up --build
```

You can use the provided scripts to build and push the Docker images to your container registry.

### For Windows

```powershell
./build_and_push.ps1
```

### For Linux/macOS

```bash
chmod +x build_and_push.sh
./build_and_push.sh
```
