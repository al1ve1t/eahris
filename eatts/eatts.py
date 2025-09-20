import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from model import synthesize_msg
import uuid
import configparser
from benchmark import start_server

app = FastAPI()

class Request(BaseModel):
    text: str
    emo: str
    email: str

@app.post("/")
async def generate_wav(request: Request):
    unique_filename = f"output_{uuid.uuid4().hex}"
    output_path = os.path.join(request.email, unique_filename)
    synthesize_msg({"emo": request.emo, "text": request.text}, output_path="../tts_output/" + output_path + ".wav")
    return JSONResponse(content={"wav_path": output_path})

def start_http_api():
    uvicorn.run(app, host="0.0.0.0", port=8080)

# Load configuration
config = configparser.ConfigParser()
config.read("../config.ini")
is_benchmark_baseline = config.getboolean("baseline", "IsBenchmarkBaseline", fallback=False)

if is_benchmark_baseline:
    start_server()
else:
    start_http_api()
