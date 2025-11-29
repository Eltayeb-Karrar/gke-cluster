# Second Part: Provision the cloud

## What will be provisioned
In this section I build a small infrastructure for GCP that provides the following:

1. In Project VPC
2. Subnetwork with sub-cidr for pod networks
3. Kubernetes cluster (Dropped default node_pool)
4. Kubernetes Node_Pool
5. NAT With Route rules to unified egress traffic IP
6. GCS Bucket for assets store

## How the infra sync with other?
I Set a backend store in GCS (Manually created bucket) to store state and allow multiple team member to work together with lock mechanism to ensure consistancy

## How to run
1. Make sure that the service account is provided in root directory level with name `thm-assess-sa.json`
2. Initilize the providers by `terraform init`
3. Validate the plan by `terraform plan`
4. Once you're ready to apply `terraform apply`

## Others
I Bring my own Domain and connect it later to Ingress Load Balancer(will be automatically created once add ingress controller)