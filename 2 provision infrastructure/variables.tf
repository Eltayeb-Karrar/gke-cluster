variable "project_id" {
  description = "The project ID to host the resources"
  type        = string
  default     = "thmanyah-assessment"
}

variable "region" {
  description = "The region to host the resources"
  type        = string
  default     = "europe-west1"
}

variable "service_account_file" {
  description = "The path to the service account key file"
  type        = string
  default     = "../thm-assess-sa.json"
}
