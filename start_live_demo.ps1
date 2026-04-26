# Start Nocturn AI LIVE Sales Demo (Ngrok + Twilio)

Write-Host "🚀 Starting Nocturn AI LIVE Demo Environment..." -ForegroundColor Cyan

# Check for Twilio Config
if (-not $env:TWILIO_ACCOUNT_SID -and (Test-Path ".env.demo")) {
    $envContent = Get-Content ".env.demo" -Raw
    if ($envContent -notmatch "TWILIO_PHONE_NUMBER=\S+") {
        Write-Warning "⚠️ TWILIO_PHONE_NUMBER is not set in .env.demo!"
        Write-Warning "   The backend will still start, but Live WhatsApp will not function."
        Write-Warning "   Please update .env.demo with your Twilio Sandbox credentials."
        Write-Host "   Press any key to continue anyway or Ctrl+C to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Fetch INTERNAL_SECRET from GCP Secret Manager for the Baileys bridge
Write-Host "`n🔐 Fetching Baileys bridge INTERNAL_SECRET from Secret Manager..." -ForegroundColor Yellow
$env:DEMO_INTERNAL_SECRET = (gcloud secrets versions access latest --secret=INTERNAL_SECRET --project=nocturn-ai-487207 2>&1).Trim()
if ([string]::IsNullOrWhiteSpace($env:DEMO_INTERNAL_SECRET)) {
    Write-Warning "⚠️  Could not fetch INTERNAL_SECRET — Baileys bridge auth will be empty. Ensure gcloud is authenticated."
} else {
    Write-Host "   ✓ INTERNAL_SECRET loaded" -ForegroundColor Green
}

# 1. Bring up the stack
Write-Host "`n🐳 Bringing up the Demo Stack on port 8001..." -ForegroundColor Yellow
docker-compose -f docker-compose.demo.yml up -d --build

# 2. Seed Data
Write-Host "`n🌱 Seeding Demo Data with Live Twilio Configuration..." -ForegroundColor Yellow
$env:PYTHONPATH = "backend"
# Load .env.demo into process space for the seeder
Get-Content .env.demo | Where-Object { $_ -match "^[^#]*=" } | ForEach-Object {
    $name, $value = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim(), 'Process')
}

python backend/seed_demo_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to seed data."
    exit $LASTEXITCODE
}

# 2b. Seed shadow pilot demo data (7-day synthetic observation for GM dashboard demo)
Write-Host "`n🔍 Seeding Shadow Pilot Demo Data (7-day observation)..." -ForegroundColor Yellow
python backend/seed_shadow_pilot_demo.py
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Shadow pilot seed failed — demo will work but GM dashboard won't have data."
}

# 3. Instructions
Write-Host "`n✅ Live Demo Environment Ready!" -ForegroundColor Green
Write-Host "---------------------------------------------------"
Write-Host "Frontend UI:  http://localhost:3001"
Write-Host "Backend API:  http://localhost:8001"
Write-Host "Admin User:   demo@nocturnai.com"
Write-Host "Admin Pass:   demo2026"
Write-Host "---------------------------------------------------"
Write-Host "🌍 QUICK START NGROK INSTRUCTIONS:" -ForegroundColor Magenta
Write-Host "---------------------------------------------------"
Write-Host "1. Open a new terminal."
Write-Host "2. Run: ngrok http 8001"
Write-Host "3. Note the Forwarding URL (e.g., https://xyz.ngrok.app)"
Write-Host "4. Go to Twilio Console -> Messaging -> Try it out -> Send a WhatsApp message"
Write-Host "5. Paste this exactly into the 'Sandbox Configuration' webhook field:"
Write-Host "   https://<your-ngrok-url>/api/v1/webhook/twilio/whatsapp"
Write-Host "6. Save, and text your join code to the Twilio number!"
Write-Host "---------------------------------------------------"
