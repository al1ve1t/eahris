import torch
from eatts.eatts import setup_tts, synthesize
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

CHECKPOINT_DIR = "/Users/elnuralimirzayev/Thesis/notebooks/eahris/resource/eatts_checkpoint/tts_model_4in1"

if __name__ == "__main__":
    model, config = setup_tts(CHECKPOINT_DIR)
    synthesize(config, "neu", "Hello, how are you?", "./output.wav")
