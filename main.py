from fastapi import FastAPI, Request
import uvicorn
import json

app = FastAPI()

@app.post("/webhook")
async def instagram_webhook(request: Request):
    payload = await request.json()
    print("Yangi trigger keldi:", json.dumps(payload, indent=2))
    return {"status": "OK"}

# Bu qismni terminaldan ishga tushirasan, VSCode ichida emas
# Terminalda: uvicorn main:app --reload
