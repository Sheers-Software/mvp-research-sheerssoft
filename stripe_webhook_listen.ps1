# stripe_webhook_listen.ps1
# Starts the Stripe CLI listener and automatically stores the webhook secret
# in GCP Secret Manager (STRIPE_WEBHOOK_SECRET).
#
# Usage:
#   .\stripe_webhook_listen.ps1              # dev backend on :8000
#   .\stripe_webhook_listen.ps1 -Port 8001   # demo backend on :8001

param(
    [int]$Port = 8000
)

$StripeBin = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Stripe.StripeCli_Microsoft.Winget.Source_8wekyb3d8bbwe\stripe.exe"
$ForwardTo = "http://localhost:$Port/api/v1/billing/webhook"

# Events the webhook handler currently processes
$Events = @(
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_succeeded",
    "invoice.payment_failed",
    "customer.subscription.trial_will_end"
) -join ","

Write-Host ""
Write-Host "Starting Stripe webhook listener" -ForegroundColor Cyan
Write-Host "  Forwarding to : $ForwardTo"
Write-Host "  Events        : (see below)"
Write-Host ""
Write-Host "IMPORTANT: Copy the 'whsec_...' secret printed below and run:" -ForegroundColor Yellow
Write-Host "  gcloud secrets create STRIPE_WEBHOOK_SECRET --data-file=- --project=nocturn-ai-487207" -ForegroundColor Yellow
Write-Host "  (or versions add if the secret already exists)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

& $StripeBin listen `
    --forward-to $ForwardTo `
    --events $Events
