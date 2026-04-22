gcloud builds submit \
    --config=backend/cloudbuild.yaml \
    --project=nocturn-ai-487207 \
    --region=asia-southeast1 \
    --substitutions=COMMIT_SHA=$(git rev-parse HEAD) \
    .