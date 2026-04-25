import express from 'express'
import { SessionManager } from './session-manager'
import { EventForwarder } from './event-forwarder'

const app = express()
app.use(express.json())

const forwarder = new EventForwarder()
const manager = new SessionManager(forwarder)

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 'http://localhost:8000'
const INTERNAL_SECRET = process.env.INTERNAL_SECRET || ''

async function loadActiveSessions() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/internal/shadow-active-properties`, {
      headers: { 'X-Internal-Secret': INTERNAL_SECRET }
    })
    if (!res.ok) {
      console.log('[Startup] Backend not ready, skipping session reload')
      return
    }
    const { properties } = await res.json() as { properties: Array<{slug: string, shadow_pilot_phone: string}> }
    console.log(`[Startup] Loading ${properties.length} active shadow pilot sessions`)
    for (const p of properties) {
      if (p.slug && p.shadow_pilot_phone) {
        await manager.startSession(p.slug, p.shadow_pilot_phone)
      }
    }
  } catch (err) {
    console.error('[Startup] Failed to load active sessions:', (err as any).message)
  }
}

// Internal API (called by FastAPI backend)
app.post('/internal/start-session', async (req, res) => {
  const { property_slug, property_phone } = req.body
  if (!property_slug || !property_phone) {
    return res.status(400).json({ error: 'property_slug and property_phone required' })
  }
  await manager.startSession(property_slug, property_phone)
  res.json({ status: 'starting' })
})

app.post('/internal/stop-session', (req, res) => {
  const { property_slug } = req.body
  manager.stopSession(property_slug)
  res.json({ status: 'stopped' })
})

// Admin QR polling (polled by frontend)
app.get('/qr/:propertySlug', (req, res) => {
  const qr = manager.getQR(req.params.propertySlug)
  const status = manager.getStatus(req.params.propertySlug)
  res.json({ qr_base64: qr, status })
})

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' })
})

const PORT = parseInt(process.env.PORT || '3001', 10)
app.listen(PORT, () => {
  console.log(`Baileys bridge running on :${PORT}`)
  loadActiveSessions()
})
