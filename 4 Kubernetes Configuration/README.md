# Fourth: Prepare the cluster
In this section I applied certain resources to
1. Connect to secret manager and obtain secret for Cert-Manager challenges (DNS through cloudflare)
2. Provision ClusterIssuer so I can use it later with certificates (TLS)

## Before you can proceed with apply these resources to cluster you need to add the 
You need to add Service account as a way to make secret-operator to connect to Secret Manager in GCP

Run this command in root level directory to onbaord service account to cert-manager for secret operator operations
```
kubectl create secret generic gcp-sa-key --from-file=secret-key.json=./thm-assess-sa.json --namespace=cert-manager
```

**Note: You have to make sure you have add the secret in GCP secret manager for cloudflare API Token that used in cluster issuer**

## Apply the resources
in this directory level run
```
kubectl apply -f ./SecretOperatorConfig/
kubectl apply -f ./CertManagerConfig/
```

### By this you're now onboard the secrets operator and cert manager, let's continues