import axios from 'axios'

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 'http://localhost:8000'
const INTERNAL_SECRET = process.env.INTERNAL_SECRET || ''

export class EventForwarder {
  private async post(path: string, payload: object): Promise<void> {
    try {
      await axios.post(`${BACKEND_URL}${path}`, payload, {
        headers: { 'X-Internal-Secret': INTERNAL_SECRET },
        timeout: 5000,
      })
    } catch (err) {
      console.error(`[EventForwarder] Failed to POST ${path}:`, (err as any).message)
    }
  }

  async sendMessageEvent(event: {
    event_type: 'message.received' | 'message.sent'
    property_slug: string
    sender_jid: string
    message_id: string
    content_preview: string | null
    timestamp_unix: number
    has_media: boolean
  }): Promise<void> {
    await this.post('/api/v1/internal/shadow-event', event)
  }

  async sendSessionStatus(
    propertySlug: string,
    status: string,
    qrBase64: string | null
  ): Promise<void> {
    await this.post('/api/v1/internal/shadow-session-status', {
      property_slug: propertySlug,
      status,
      qr_base64: qrBase64,
    })
  }

  async sendHeartbeat(propertySlug: string): Promise<void> {
    await this.post('/api/v1/internal/shadow-heartbeat', {
      property_slug: propertySlug,
    })
  }
}
