# Third Part: Provision core infrastructure components
## What will be done in this section
In this part We will install the essential component for our infrastructure

1. nginx-ingress controller: will run LB that associated with DNS so will accept and act as reverse-proxy for the cluster based in ingress rules
2. cert-manager: automate create/rotate/renew SSL/TLS Certificate
3. secret-operator: My faviourt secret manager it allow sync secret with external secret store/manager such as (Vault/GCP Secret Manager,etc...)
4. prometheus-operator: Will install promethus TSDB, Grafana, and alert manager to give us ability to trace metrics and add alerts
5. loki: log indexer to store app/pod/cluster components logs
6. Promtail(Log Collector): Will Collect logs from cluster pods/components and ship it labeled to loki for indexing

## How to run
You can provide this infrastructure

```
helm upgrade --install ingress-nginx .\nginx-ingress-wrapper\ -n ingress-nginx --create-namespace
helm upgrade --install cert-manager .\cert-manager-wrapper\ -n cert-manager --create-namespace
helm upgrade --install secret-operator .\external-secrets-wrapper\ -n secret-operator --create-namespace
helm upgrade --install kube-prom-stack .\prometheus-operator-wrapper\ -n observability --create-namespace
helm upgrade --install loki .\loki-wrapper\ -n loki --create-namespace
helm upgrade --install promtail .\log-collector-wrapper\ -n promtail --create-namespace 
```