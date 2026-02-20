import uuid
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from app.services.conversation import process_guest_message

logger = structlog.get_logger()
router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, property_id: str, session_id: str):
    """
    WebSocket endpoint for the web chat widget.
    URL: ws://domain/api/v1/ws/chat?property_id=...&session_id=...

    Protocol:
      Client → Server:  {"message": "text...", "property_id": "...", "session_id": "..."}
      Server → Client:  {"type": "typing"}
      Server → Client:  {"type": "ai_response", "response": "text..."}
      Server → Client:  {"type": "error", "detail": "..."}
    """
    await websocket.accept()

    from app.database import async_session, set_db_context

    logger.info("WEBSOCKET_CONNECT", session_id=session_id, property_id=property_id)

    try:
        pid = uuid.UUID(property_id)
        guest_identifier = f"web:{session_id}"

        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            # Accept both "message" (new widget) and "text" (legacy compat)
            user_text = payload.get("message") or payload.get("text")
            if not user_text:
                continue

            # Send typing indicator
            await websocket.send_text(json.dumps({"type": "typing"}))

            # Process with AI
            async with async_session() as db:
                await set_db_context(db, property_id)

                result = await process_guest_message(
                    db=db,
                    property_id=pid,
                    guest_identifier=guest_identifier,
                    channel="web",
                    message_text=user_text,
                    guest_name=payload.get("guest_name", "Web Guest"),
                )

                response_text = result.get("response", "Sorry, I could not process that.")

                # Send AI response
                await websocket.send_text(json.dumps({
                    "type": "ai_response",
                    "response": response_text,
                }))

    except WebSocketDisconnect:
        logger.info("WEBSOCKET_DISCONNECT", session_id=session_id)
    except Exception as e:
        logger.error("WEBSOCKET_ERROR", error=str(e), session_id=session_id)
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "detail": "An internal error occurred.",
            }))
            await websocket.close()
        except Exception:
            pass
