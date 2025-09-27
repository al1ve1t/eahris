from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import uvicorn
import requests
from urllib.parse import unquote

def wait_for_tts_finish(tts_client):
    """
    Waits for the TTS client to finish processing.
    This function blocks until the TTS client signals that it has finished.
    """
    def callback(ch, method, properties, body):
        print("Received finish signal from TTS.")
        # Send file back to the frontend
    tts_client.wait_for_finish(callback)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    speaker: str
    text: str
    def __getitem__(self, item):
        return getattr(self, item)
    
class ChatMessageFromNICO(ChatMessage):
    speaker: str = "NICO"
    emo: str

class ChatHistoryRequest(BaseModel):
    chat_history: List[ChatMessage]
    name: str

@app.post("/process_chat")
async def process_chat(request: ChatHistoryRequest):
    chat_history = request.chat_history
    name = request.name
    # Process request: run spcl and call eatts
    emo_history = spcl_client([chat_history])
    llm_response = llm_client.chat(chat_history[-1]["text"], chat_history)
    # Make API request to localhost:8080 with text, emo, and email
    payload = {
        "text": llm_response.output_text,
        "emo": emo_history[-1],
        "name": name
    }
    try:
        api_response = requests.post("http://localhost:8080/", json=payload)
        api_response.raise_for_status()
        wav_path = api_response.json().get("wav_path")
    except Exception as e:
        print(f"Error calling TTS API: {e}")
        wav_path = None
    chat_history.append(ChatMessageFromNICO(text=llm_response.output_text, emo=emo_history[-1]))
    response = {
        "chat_history": [msg.dict() for msg in chat_history],
        "name": name
    }
    headers = {
        "X-Audio-File": wav_path,
        "Access-Control-Expose-Headers": "x-audio-file"
    }
    return JSONResponse(content=response, headers=headers)

@app.get("/tts_output/{name}/{output_path}")
def get_audio(name: str, output_path: str):
    filename_decoded = "tts_output/" + unquote(name) + "/" + output_path + ".wav"
    file_path = os.path.join(os.getcwd(), filename_decoded)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav", filename=filename_decoded)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

def start_backend(spcl, eatts, llm):
    global spcl_client, eatts_client, llm_client
    spcl_client = spcl
    eatts_client = eatts
    llm_client = llm
    uvicorn.run(app, host="0.0.0.0", port=8000)
