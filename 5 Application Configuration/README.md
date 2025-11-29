# Fifth: Provision Applications

Now it's time to tell the cluster how to run the applications

## What will we do now

In this section we will be work on provisioning the applications and all related resources 

will utilize **kustomization** to make configuration dynamic and less error prone

## Apply the configuration
just run in this directory level
```
kubectl apply -k .
```
And all resources will be provisioned automatically

## Understand the configurations
For each service we built a collection of resources
the use of kustomization is to allow reusability and patching the resource definition based on desired environment

Components:
1. api-service: contain all necessary resources to provision the service (api service)
2. iam-service: contain all necessary resources to provision the service (iam service)
3. image-service: contain all necessary resources to provision the service (image service)
4. mongodb: contain all necessary resources to provision mongodb V8 (Required as a primary DB)
5. `_Components/SharedSecrets`: Included when needed as a component for provision the secret 

## Chicken and Egg problem with secret manager :)
In this configuration we need to make sure that the service account for access to secret provisioned in each namespace as required by secret operator 

refer to `./_Components/SharedSecret/Kustomization.yaml`

**Make sure that `secret-key.json` which is copy of prev. file `thm-assess-sa.json` is exists in ``./_Components/SharedSecret/`**

__**Note:**__ This's not the best way to connect in Cluster to secret in GCP specially with GKE, this has been done to make things easier