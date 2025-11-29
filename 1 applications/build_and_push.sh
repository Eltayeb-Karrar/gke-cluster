#!/bin/bash

# This script builds and pushes Docker images for all services to the Google Artifact Registry.
#
# Prerequisites:
# 1. Google Cloud SDK (gcloud) installed and authenticated.
# 2. Docker installed and running.
# 3. You must be in the '1 applications' directory to run this script.
#
# Usage:
# ./build_and_push.sh

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
REGISTRY_HOST="europe-west1-docker.pkg.dev"
PROJECT_ID="thmanyah-assessment"
REPOSITORY="thm-assessment"
IMAGE_PREFIX="${REGISTRY_HOST}/${PROJECT_ID}/${REPOSITORY}"
SERVICES=("api-service" "iam-service" "image-service")

# --- Main Script ---

# 1. Authenticate Docker with Artifact Registry
echo "--- Authenticating Docker with gcloud ---"
gcloud auth configure-docker ${REGISTRY_HOST}
echo "Authentication complete."
echo

# 2. Build, Tag, and Push images for each service
for SERVICE in "${SERVICES[@]}"; do
  SERVICE_DIR="./${SERVICE}"
  LOCAL_TAG="assessment-${SERVICE}:latest"
  REMOTE_TAG="${IMAGE_PREFIX}/assessment-${SERVICE}:latest"

  echo "--- Processing service: ${SERVICE} ---"

  # Build the image
  echo "Building Docker image: ${LOCAL_TAG} from ${SERVICE_DIR}"
  docker build -t ${LOCAL_TAG} "${SERVICE_DIR}"

  # Tag the image
  echo "Tagging image to: ${REMOTE_TAG}"
  docker tag ${LOCAL_TAG} ${REMOTE_TAG}

  # Push the image
  echo "Pushing image: ${REMOTE_TAG}"
  docker push ${REMOTE_TAG}

  echo "--- Finished processing ${SERVICE} ---"
  echo
done

echo "All images have been built and pushed successfully."
