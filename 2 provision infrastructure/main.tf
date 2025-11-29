terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    bucket      = "tha-tf-state-bucket" //Manually created
    prefix      = "terraform/state"
    credentials = "../thm-assess-sa.json"
  }
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.service_account_file)
}

resource "google_compute_network" "vpc" {
  name                    = "assessment-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnetwork" {
  name          = "assessment-subnet"
  ip_cidr_range = "10.0.0.0/22"
  region        = var.region
  network       = google_compute_network.vpc.self_link
  secondary_ip_range {
    range_name    = "pods-range"
    ip_cidr_range = "10.48.0.0/14"
  }
  secondary_ip_range {
    range_name    = "services-range"
    ip_cidr_range = "10.52.0.0/20"
  }
}

resource "google_compute_router" "router" {
  name    = "tha-router"
  region  = var.region
  network = google_compute_network.vpc.self_link
}

resource "google_compute_router_nat" "nat" {
  name                               = "tha-nat"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

resource "google_container_cluster" "primary" {
  name               = "assessment-cluster"
  location           = var.region
  initial_node_count = 1
  network            = google_compute_network.vpc.self_link
  subnetwork         = google_compute_subnetwork.subnetwork.self_link
  networking_mode    = "VPC_NATIVE"

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods-range"
    services_secondary_range_name = "services-range"
  }

  network_policy {
    enabled = true
  }

  node_config {
    disk_size_gb = 30
    disk_type    = "pd-standard"
  }

  remove_default_node_pool = true
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 1 //per region zone total 3

  node_config {
    machine_type = "e2-standard-2"
    disk_size_gb = 50
    disk_type    = "pd-standard"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_storage_bucket" "assets_store" {
  name                        = "tha-assets-store"
  location                    = var.region
  uniform_bucket_level_access = true
}