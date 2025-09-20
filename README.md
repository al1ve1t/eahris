# Setup Instructions for Inference

Because of the depencency conflicts, the project utilizes two virtual environments: one for spcl model, another for xtts. 

(Tested on MacOS Sequoia 15.6)

## Setup venv for SPCL

1. **Install Python 3.8.19 (or similar version):**  
    Ensure you have Python 3.8.19 or a compatible version installed. You can download it from the [official Python website](https://www.python.org/downloads/).

2. **Create a Virtual Environment:**  
    Run the following commands to create and activate a virtual environment:
    ```bash
    python3 -m venv .venv_spcl
    ```

3. **Install Requirements:**  
    Install the required dependencies using `requirements.txt`:
    ```bash
    pip install -r requirements_spcl.txt
    ```

## Setup venv for XTTS-v2

4. **Install Python 3.10.14 (or similar version)**

5. **Create a Virtual Environment:**
    ```bash
    python3 -m venv .venv_xtts
    ```
6. **Install requirements:**
    ```bash
    pip install -r requirements_xtts.txt
    ```

## Run Docker compose file

7. **Run the command:**
    ```bash
    docker-compose up -d
    ```

## Activate TTS venv and run TTS service in additional terminal

8. **Run the command:**
    ```bash
    source .venv_xtts/bin/activate;
    cd ./eatts;
    python3 eatts.py
    ```

## Chech out the config.ini

9. Make sure that: 
    ```ini
    [baseline]
    IsBenchmarkBaseline = 'yes'
    [secrets]
    OpenAiApiKey = yourApiKey
    [runtimes]
    TtsRuntime = "pathToYour-./venv_tts/bin/python
    ```
## Upload and install resources:

10. Install TTS model

Download XTTS-v2 model and move it in ```resource/eatts_checkpoint/tts_model_4in1```

11. (Optional) Replace reference audios in ```iemocap_refaudios```

12. Install SPCL model

Download the model from here: https://huggingface.co/al1ve1t/eahis_spcl_checkpoint \
Repack content into ```resource/spcl_checkpoint```

13. Run Project


