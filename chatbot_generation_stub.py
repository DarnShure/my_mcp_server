from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

import uvicorn
import json
import asyncio

app = FastAPI()


@app.post("/api/v1/{index_name}/chats/{chat_name}/generate")
async def generate(index_name: str, chat_name: str, request: Request):
    # Accept empty request body
    try:
        await request.body()
    except Exception:
        pass

    async def event_stream():
        for _ in range(15):
            yield "data: . \n\n"
            await asyncio.sleep(0.05)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6006)