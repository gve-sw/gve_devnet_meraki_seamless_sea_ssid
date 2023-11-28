from fastapi import APIRouter, Request
from meraki_funcs import handle_webhook

router = APIRouter()


@router.post("/webhook")
async def webhook_handler(request: Request) -> object:
    data = await request.json()
    dashboard = request.app.state.meraki_dashboard
    return await handle_webhook(dashboard, data)
