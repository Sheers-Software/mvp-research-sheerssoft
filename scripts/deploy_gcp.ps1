$PROJECT_ID = "nocturn-ai-487207"
$REGION = "asia-southeast1"
$BACKEND_SERVICE = "nocturn-backend"
$FRONTEND_SERVICE = "nocturn-frontend"
$SA = "nocturn-cloud-run@nocturn-ai-487207.iam.gserviceaccount.com"

# Database is Supabase — DATABASE_URL is stored in GCP Secret Manager and
# fetched by the app at startup via config.py. No Cloud SQL instance needed.

# 1. Enable required GCP services
Write-Output "Enabling GCP services..."
cmd /c "gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com --project $PROJECT_ID --quiet"

# 2. Deploy Backend
Write-Output "Deploying Backend..."
cmd /c "gcloud run deploy $BACKEND_SERVICE --source ./backend --platform managed --region $REGION --project $PROJECT_ID --allow-unauthenticated --service-account $SA --set-env-vars ""ENVIRONMENT=production"" --quiet"

# 3. Get Backend URL
$BACKEND_URL = gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format 'value(status.url)' --project $PROJECT_ID --quiet
Write-Output "Backend URL: $BACKEND_URL"

# 4. Deploy Frontend
Write-Output "Deploying Frontend..."
cmd /c "gcloud run deploy $FRONTEND_SERVICE --source ./frontend --platform managed --region $REGION --project $PROJECT_ID --allow-unauthenticated --service-account $SA --set-env-vars ""NEXT_PUBLIC_API_URL=$BACKEND_URL"" --quiet"

Write-Output "Deployment Complete!"
