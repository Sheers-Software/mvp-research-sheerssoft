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
