# First: Application Part

This section I built 3 serivces written in (Node.JS, and Python)

1. API-Service: Mocking CRUD Operations for customer data
2. IAM-Service: Work as identity management service for Authentication/Authorization (Imagine it's like KeyCloak, Authentik, et..)
3. Image-Service: Deal With Object storage (GCS for now)

## How to run

**First** Make sure you're included `thm-assess-sa.json` file in root directory level because it will be utilized from image-service to connect to GCS Buckets

**Second** Run the docker compose `docker-compose.yaml` as follow:
```
docker compose up --build     #Run this in this ./1 applications/ level
```

## How to push my changes
Once you finish modification you can upload manually to images registery or you can just run my script to build and push automatically
### For Windows

```
build_and_push.ps   # PowerShell Script
```

## For POSIX Based

```
sh build_and_push.sh   # Shell script
# OR
build_and_push.sh       # Consider to change the execution flag +x
```


All the best ❤️