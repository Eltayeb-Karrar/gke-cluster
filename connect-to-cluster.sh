gcloud auth activate-service-account --key-file=./thm-assess-sa.json
gcloud container clusters get-credentials assessment-cluster --region europe-west1 --project thmanyah-assessment