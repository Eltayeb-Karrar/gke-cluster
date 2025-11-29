output "gke_cluster_name" {
  description = "The name of the GKE cluster"
  value       = google_container_cluster.primary.name
}

output "gcs_assets_store_bucket_name" {
  description = "The name of the GCS assets store bucket"
  value       = google_storage_bucket.assets_store.name
}
