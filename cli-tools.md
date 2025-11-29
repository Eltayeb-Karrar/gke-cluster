# Please make sure you install the following
1. Terraform cli
2. gcloud cli
3. gcloud plugin auth for kubernetes
4. kustomize optional but preffered to allow debugging application manifest
5. helm cli
6. kubectl 1.33 or 1.34

# Supporting Scripts/Docs

`200s-repear.sh` you can use it for mocking 200 request to api-service
just need to change the token with `curl` request

`400s-repear.sh` you can use it for mocking 400 request to api-service

---

`connect-to-cluster.sh` Once you have installed CLI tools then run this script to connect and give you access to cluster through kubectl (it will add conext for connecting to cluster)