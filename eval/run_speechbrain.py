import os
import pandas as pd
import csv
import whisper
from alive_progress import alive_bar
from speechbrain.inference.interfaces import foreign_class
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from speechbrain.utils.edit_distance import accumulatable_wer_stats
from speechbrain.utils.metric_stats import ErrorRateStats

classifier = foreign_class(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    pymodule_file="custom_interface.py",
    classname="CustomEncoderWav2vec2Classifier",
)
asr = whisper.load_model("base.en")

def run_speechbrain(report_path: str, eval_report_path: str):
    # Count the number of files in the report_path directory
    file_count = len(os.listdir(os.path.dirname(report_path))) - 1  # Exclude the CSV file itself
    # Read the CSV file from report_path
    with open(report_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        actual_labels = []
        predicted_labels = []
        total = 0
        correct = 0
        ref_sentences = []
        hyp_sentences = []
        with alive_bar(file_count, title="Processing") as bar:
            for row in reader:
                bar()
                total += 1
                out_prob, score, index, text_lab = classifier.classify_file(
                    row["output_wav"]
                )
                asr_result = asr.transcribe(row["output_wav"], fp16=False)
                ref_sentences.append(row["text"])
                hyp_sentences.append(asr_result["text"])
                predicted_labels.append(text_lab[0])
                actual_labels.append(row["initial_emo"])
                if row["initial_emo"] == text_lab[0]:
                    correct += 1
        accuracy = correct / total
        print(f"Accuracy: {accuracy:.2f}")
        print(f"WER: {accumulatable_wer_stats(ref_sentences, hyp_sentences)}")

        # --- CER (character-level) ---
        # split_tokens=True -> internally splits word tokens into characters
        ref_words = [s.split() for s in ref_sentences]
        hyp_words = [s.split() for s in hyp_sentences]
        cer_stats = ErrorRateStats(split_tokens=True)
        cer_stats.clear()
        cer_stats.append(
            ids=list(range(len(ref_words))),
            predict=hyp_words,
            target=ref_words,
        )
        cer_summary = cer_stats.summarize()
        # The key is still named 'WER' in API, but with split_tokens=True this is CER.
        print(f"CER: {cer_summary['WER']:.2f}%")

    # Generate and save the report
    plt.figure(figsize=(12, 8))

    # Plot confusion matrix
    plt.subplot(2, 2, 1)
    ConfusionMatrixDisplay.from_predictions(
        list(actual_labels),
        list(predicted_labels),
        ax=plt.gca(),
    )
    plt.title("Confusion Matrix for Predicted vs Actual Emotions")
    plt.xlabel("Predicted Emotion")
    plt.ylabel("Actual Emotion")

    # Plot horizontal bar with actual labels
    actual_labels_dict = {"ang": 0, "hap": 0, "neu": 0, "sad": 0}
    for label in actual_labels:
        actual_labels_dict[label] += 1
    plt.subplot(2, 2, 2)
    bars = plt.barh(list(actual_labels_dict.keys()), list(actual_labels_dict.values()), color='blue')
    plt.bar_label(bars)
    plt.title("Actual Labels")
    plt.gca().invert_yaxis()
    # Plot vertical bar with predicted labels
    predicted_labels_dict = {"ang": 0, "hap": 0, "neu": 0, "sad": 0}
    for label in predicted_labels:
        predicted_labels_dict[label] += 1
    plt.subplot(2, 2, 3)
    bars = plt.bar(list(predicted_labels_dict.keys()), list(predicted_labels_dict.values()), color='blue')
    plt.bar_label(bars)
    plt.title("Predicted Labels")
    plt.tick_params(labelbottom=False, labeltop=True)
    plt.gca().invert_yaxis()
    

    # Save the report to a file
    plt.tight_layout()
    plt.savefig(eval_report_path)
    plt.close()

if __name__ == "__main__":
    run_speechbrain("/Users/elnuralimirzayev/Thesis/notebooks/eahris/baselines/benchmark/tts_output/20250908_022659/feed.csv", 
                "/Users/elnuralimirzayev/Thesis/notebooks/eahris/report2.png")
# /Users/elnuralimirzayev/Thesis/notebooks/eahris/tts_output/20250630_171757/feed.csv <-- BEST