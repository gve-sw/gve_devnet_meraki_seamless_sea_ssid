from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook")
async def webhook_handler(request: Request) -> object:
    data = await request.json()
    meraki_operations = request.app.state.meraki_operations
    return await meraki_operations.handle_webhook(data)