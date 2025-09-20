import os
import pika
import soundfile as sf
import json
from pika.adapters.blocking_connection import BlockingChannel
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../resource/eatts_checkpoint/tts_model_4in1")
AUDIOREF_PATH = os.path.join(os.path.dirname(__file__), "../iemocap_refaudios")
SAMPLE_RATE = 22000  # 22000 32750

def setup_tts(checkpoint_dir: str):
    config = XttsConfig()
    config.load_json(os.path.join(checkpoint_dir, "config.json"))
    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=checkpoint_dir,
        eval=True,
        vocab_path=os.path.join(checkpoint_dir, "vocab.json"),
    )
    model.cpu()
    return model, config

model, config = setup_tts(MODEL_PATH)

def synthesize(config, emo: str, text: str, output_path = None):
    outputs = model.synthesize(
        text,
        config,
        speaker_wav=os.path.join(AUDIOREF_PATH, emo + ".wav"),
        gpt_cond_len=3,
        language="en",
    )
    raw_audio = outputs["wav"]
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "../tts_output/voice.wav")
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    sf.write(output_path, raw_audio, SAMPLE_RATE)

def synthesize_msg(msg, output_path=None):
    emo = msg["emo"]
    text = msg["text"]
    if not emo or not text:
        raise ValueError("Missing 'emo' or 'text' in the message.")
    synthesize(config, emo, text, output_path)