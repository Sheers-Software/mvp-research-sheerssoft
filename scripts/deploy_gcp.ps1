$PROJECT_ID = "nocturn-ai-487207"
$REGION = "us-central1"
$DB_INSTANCE_NAME = "sheerssoft-db"
$DB_NAME = "sheerssoft"
$DB_USER = "sheerssoft"
$DB_PASS = "sheerssoft_prod_password_123" # In a real scenario, use Secret Manager
$BACKEND_SERVICE = "sheerssoft-backend"
$FRONTEND_SERVICE = "sheerssoft-frontend"

# 1. Enable Services (Just in case)
cmd /c "gcloud services enable run.googleapis.com sqladmin.googleapis.com compute.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com --project $PROJECT_ID"

# 2. Create Cloud SQL Instance
echo "Creating Cloud SQL Instance..."
# Check if instance exists first to avoid error
$instanceExists = gcloud sql instances describe $DB_INSTANCE_NAME --project=$PROJECT_ID 2>&1
if ($LASTEXITCODE -ne 0) {
    cmd /c "gcloud sql instances create $DB_INSTANCE_NAME --database-version=POSTGRES_15 --cpu=1 --memory=3840MiB --region=$REGION --project=$PROJECT_ID --root-password=$DB_PASS"
}
else {
    echo "Instance $DB_INSTANCE_NAME already exists."
}

# 3. Create Database and User
echo "Creating Database and User..."
cmd /c "gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME --project=$PROJECT_ID"
cmd /c "gcloud sql users create $DB_USER --instance=$DB_INSTANCE_NAME --password=$DB_PASS --project=$PROJECT_ID"

# 4. Deploy Backend
echo "Deploying Backend..."
$CONNECTION_NAME = "${PROJECT_ID}:${REGION}:${DB_INSTANCE_NAME}"
$DB_URL = "postgresql+asyncpg://${DB_USER}:${DB_PASS}@/${DB_NAME}?unix_sock=/cloudsql/${CONNECTION_NAME}"

cmd /c "gcloud run deploy $BACKEND_SERVICE --source ./backend --platform managed --region $REGION --project $PROJECT_ID --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars ""DATABASE_URL=$DB_URL,OPENAI_API_KEY=$env:OPENAI_API_KEY,ENVIRONMENT=production"""

# 5. Get Backend URL
$BACKEND_URL = gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format 'value(status.url)' --project $PROJECT_ID
echo "Backend URL: $BACKEND_URL"

# 6. Deploy Frontend
echo "Deploying Frontend..."
cmd /c "gcloud run deploy $FRONTEND_SERVICE --source ./frontend --platform managed --region $REGION --project $PROJECT_ID --allow-unauthenticated --set-env-vars ""NEXT_PUBLIC_API_URL=$BACKEND_URL"""

echo "Deployment Complete!"
