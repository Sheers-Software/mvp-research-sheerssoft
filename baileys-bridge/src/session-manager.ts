import makeWASocket, {
  DisconnectReason,
  useMultiFileAuthState,
  fetchLatestBaileysVersion,
  WASocket,
} from '@whiskeysockets/baileys'
import { Boom } from '@hapi/boom'
import { EventForwarder } from './event-forwarder'
import QRCode from 'qrcode'
import * as pino from 'pino'

interface SessionState {
  socket: WASocket | null
  qrBase64: string | null
  status: 'waiting_qr' | 'connecting' | 'connected' | 'disconnected'
  lastHeartbeat: Date | null
  propertySlug: string
  propertyPhone: string
}

function extractTextContent(msg: any): string | null {
  return msg.message?.conversation
    ?? msg.message?.extendedTextMessage?.text
    ?? null
}

function hasMedia(msg: any): boolean {
  return !!(
    msg.message?.imageMessage ||
    msg.message?.videoMessage ||
    msg.message?.audioMessage ||
    msg.message?.documentMessage
  )
}

export class SessionManager {
  private sessions: Map<string, SessionState> = new Map()
  private forwarder: EventForwarder

  constructor(forwarder: EventForwarder) {
    this.forwarder = forwarder
  }

  async startSession(propertySlug: string, propertyPhone: string): Promise<void> {
    const sessionsDir = `./sessions/${propertySlug}`
    const { state, saveCreds } = await useMultiFileAuthState(sessionsDir)
    const { version } = await fetchLatestBaileysVersion()
    const logger = (pino as any).default({ level: 'silent' })

    const sessionState: SessionState = {
      socket: null,
      qrBase64: null,
      status: 'waiting_qr',
      lastHeartbeat: null,
      propertySlug,
      propertyPhone,
    }
    this.sessions.set(propertySlug, sessionState)

    const sock = makeWASocket({
      version,
      auth: state,
      printQRInTerminal: false,
      getMessage: async () => undefined,
      logger,
    })

    sessionState.socket = sock

    sock.ev.on('connection.update', async (update) => {
      const { connection, lastDisconnect, qr } = update

      if (qr) {
        sessionState.qrBase64 = await QRCode.toDataURL(qr)
        sessionState.status = 'waiting_qr'
        await this.forwarder.sendSessionStatus(propertySlug, 'waiting_qr', sessionState.qrBase64)
      }

      if (connection === 'open') {
        sessionState.status = 'connected'
        sessionState.qrBase64 = null
        sessionState.lastHeartbeat = new Date()
        await this.forwarder.sendSessionStatus(propertySlug, 'connected', null)
        console.log(`[${propertySlug}] Session connected`)
      }

      if (connection === 'close') {
        const statusCode = (lastDisconnect?.error as Boom)?.output?.statusCode
        const shouldReconnect = statusCode !== DisconnectReason.loggedOut
        sessionState.status = 'disconnected'
        await this.forwarder.sendSessionStatus(propertySlug, 'disconnected', null)

        if (shouldReconnect) {
          console.log(`[${propertySlug}] Reconnecting in 5s...`)
          setTimeout(() => this.startSession(propertySlug, propertyPhone), 5000)
        } else {
          console.log(`[${propertySlug}] Logged out. Session ended.`)
          this.sessions.delete(propertySlug)
        }
      }
    })

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
      if (type !== 'notify') return

      for (const msg of messages) {
        if (!msg.message) continue
        if (msg.key.fromMe) continue
        const senderJid = msg.key.remoteJid
        if (!senderJid || senderJid.includes('@g.us')) continue
        const content = extractTextContent(msg)
        if (content === null && !hasMedia(msg)) continue

        await this.forwarder.sendMessageEvent({
          event_type: 'message.received',
          property_slug: propertySlug,
          sender_jid: senderJid,
          message_id: msg.key.id!,
          content_preview: content ? content.substring(0, 200) : null,
          timestamp_unix: ((msg.messageTimestamp as number) || Date.now() / 1000) * 1000,
          has_media: hasMedia(msg),
        })
      }

      for (const msg of messages) {
        if (!msg.key.fromMe) continue
        if (!msg.message) continue
        const recipientJid = msg.key.remoteJid
        if (!recipientJid || recipientJid.includes('@g.us')) continue

        await this.forwarder.sendMessageEvent({
          event_type: 'message.sent',
          property_slug: propertySlug,
          sender_jid: recipientJid,
          message_id: msg.key.id!,
          content_preview: null,
          timestamp_unix: ((msg.messageTimestamp as number) || Date.now() / 1000) * 1000,
          has_media: false,
        })
      }
    })

    setInterval(async () => {
      if (sessionState.status === 'connected') {
        sessionState.lastHeartbeat = new Date()
        await this.forwarder.sendHeartbeat(propertySlug)
      }
    }, 60_000)
  }

  getQR(propertySlug: string): string | null {
    return this.sessions.get(propertySlug)?.qrBase64 ?? null
  }

  getStatus(propertySlug: string): string {
    return this.sessions.get(propertySlug)?.status ?? 'not_started'
  }

  stopSession(propertySlug: string): void {
    const session = this.sessions.get(propertySlug)
    if (session?.socket) {
      session.socket.end(undefined)
      this.sessions.delete(propertySlug)
    }
  }
}
