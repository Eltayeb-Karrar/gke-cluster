# This script builds and pushes Docker images for all services to the Google Artifact Registry.
#
# Prerequisites:
# 1. Google Cloud SDK (gcloud) installed and authenticated.
# 2. Docker installed and running.
# 3. You must be in the '1 applications' directory to run this script.
#
# Usage:
# .\build_and_push.ps1

# --- Configuration ---
$ErrorActionPreference = "Stop" # Exit immediately if a command fails.

$registryHost = "europe-west1-docker.pkg.dev"
$projectId = "thmanyah-assessment"
$repository = "thm-assessment"
$imagePrefix = "$registryHost/$projectId/$repository"
$services = @("api-service", "iam-service", "image-service")

# --- Main Script ---

# 1. Authenticate Docker with Artifact Registry
Write-Host "--- Authenticating Docker with gcloud ---"
gcloud auth configure-docker $registryHost
Write-Host "Authentication complete."
Write-Host ""

# 2. Build, Tag, and Push images for each service
foreach ($service in $services) {
    $serviceDir = "./$service"
    $localTag = "assessment-$service`:latest"
    $remoteTag = "$imagePrefix/assessment-$service`:latest"

    Write-Host "--- Processing service: $service ---"

    # Build the image
    Write-Host "Building Docker image: $localTag from $serviceDir"
    docker build -t $localTag $serviceDir

    # Tag the image
    Write-Host "Tagging image to: $remoteTag"
    docker tag $localTag $remoteTag

    # Push the image
    Write-Host "Pushing image: $remoteTag"
    docker push $remoteTag

    Write-Host "--- Finished processing $service ---"
    Write-Host ""
}

Write-Host "All images have been built and pushed successfully."
