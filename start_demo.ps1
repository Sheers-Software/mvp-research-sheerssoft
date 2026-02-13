# Start Nocturn AI Sales Demo

Write-Host "🚀 Starting Nocturn AI Demo Environment..." -ForegroundColor Cyan

# 1. Seed Data
Write-Host "🌱 Seeding Demo Data (Grand Horizon Resort)..." -ForegroundColor Yellow
$env:PYTHONPATH = "backend"
python backend/seed_demo_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to seed data."
    exit $LASTEXITCODE
}

# 2. Instructions
Write-Host "`n✅ Demo Environment Ready!" -ForegroundColor Green
Write-Host "---------------------------------------------------"
Write-Host "backend API: http://localhost:8000"
Write-Host "Frontend UI: http://localhost:3000"
Write-Host "---------------------------------------------------"
Write-Host "Credentials:"
Write-Host "   Property: Grand Horizon Resort"
Write-Host "   Phone:    601112223333"
Write-Host "---------------------------------------------------"
Write-Host "To launch the Dashboard, open http://localhost:3000 in your browser."
Write-Host "To view the Demo Script, open docs/sales_demo_script.md"
