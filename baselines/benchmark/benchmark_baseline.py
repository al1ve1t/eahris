import os
import shutil
import csv
import json
import time
from alive_progress import alive_bar
from eval.run_speechbrain import run_speechbrain

emo_map = {
    "ang": "ang",
    "hap": "hap",
    "exc": "hap",
    "sad": "sad",
    "fru": "sad",
    "neu": "neu"
}

def read_json_file(path):
    """
    Reads a JSON file from the specified path. The JSON file is expected to contain
    an array of arrays of objects with "text" and "speaker" fields. Prints the fields
    of every object.

    Args:
        path (str): The path to the JSON file.
    """
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        dialogues = []
        for array in data:
            dialogue = []
            for obj in array:
                if obj.get("label") == "fru":
                    obj["label"] = "sad"
                elif obj.get("label") == "exc":
                    obj["label"] = "hap"
                dialogue.append(obj)
            dialogues.append(dialogue)
        return dialogues

def evaluate_output(tts_client, report_path):
    # Evaluate the output
    def callback(ch, method, properties, body):
        print("Received finish signal from TTS.")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        run_speechbrain(report_path, os.path.join(os.path.dirname(__file__), f"report_{timestamp}.png",))
    # Wait for TTS finish signal to start evaluation
    tts_client.wait_for_finish(callback)

def benchmark_baseline(spcl_client, eatts_client):
    # Remove contents of tts_output directory
    tts_output_dir = os.path.join(os.path.dirname(__file__), "tts_output", time.strftime("%Y%m%d_%H%M%S"))
    if os.path.exists(tts_output_dir):
        shutil.rmtree(tts_output_dir)
    os.makedirs(tts_output_dir, exist_ok=True)
    
    tts_feed = []
    dialogues = read_json_file("spcl_test/test_data.json")
    with alive_bar(len(dialogues), title="Processing dialogues") as bar:
        for dialogue in dialogues:
            bar()
            emo_list = spcl_client([dialogue])
            for i, emo in enumerate(emo_list):
                if "label" in dialogue[i] and len(dialogue[i]["text"]) < 250:
                    tts_feed.append({
                        "text": dialogue[i]["text"],
                        "emo": emo_map[emo],
                        "initial_emo": emo_map[dialogue[i]["label"]],
                        "initial_text": dialogue[i]["text"],
                        "output_wav": os.path.join(tts_output_dir, f"{dialogue[i]['speaker']}_{i}.wav")
                    })
    eatts_client.call_tts_benchmark(tts_feed)
    # Export tts_feed to feed.csv
    output_csv_path = os.path.join(tts_output_dir, "feed.csv")
    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["text", "emo", "initial_emo", "initial_text", "output_wav"], delimiter="|")
        writer.writeheader()
        writer.writerows(tts_feed)
    evaluate_output(eatts_client, output_csv_path)