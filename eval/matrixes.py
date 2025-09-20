import os
import csv
import time
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from alive_progress import alive_bar
from run_speechbrain import run_speechbrain
from speechbrain.inference.interfaces import foreign_class

classifier = foreign_class(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    pymodule_file="custom_interface.py",
    classname="CustomEncoderWav2vec2Classifier",
)

def plot_matrix(actual_labels, predicted_labels, eval_report_path, actual_pch, predicted_pch):
    # Generate and save the report
    plt.figure(figsize=(12, 8))

    # Plot confusion matrix
    plt.subplot(2, 2, 1)
    ConfusionMatrixDisplay.from_predictions(
        list(actual_labels),
        list(predicted_labels),
        ax=plt.gca(),
    )
    plt.title(f"Confusion Matrix for {predicted_pch} vs {actual_pch} Emotions")
    plt.xlabel(f"{predicted_pch} Emotion")
    plt.ylabel(f"{actual_pch} Emotion")

    # # Plot horizontal bar with actual labels
    actual_labels_dict = {"ang": 0, "hap": 0, "neu": 0, "sad": 0}
    for label in actual_labels:
        actual_labels_dict[label] += 1
    plt.subplot(2, 2, 2)
    bars = plt.barh(list(actual_labels_dict.keys()), list(actual_labels_dict.values()), color='blue')
    plt.bar_label(bars)
    plt.title(f"{actual_pch} Labels")
    plt.gca().invert_yaxis()
    # Plot vertical bar with predicted labels
    predicted_labels_dict = {"ang": 0, "hap": 0, "neu": 0, "sad": 0}
    for label in predicted_labels:
        predicted_labels_dict[label] += 1
    plt.subplot(2, 2, 3)
    bars = plt.bar(list(predicted_labels_dict.keys()), list(predicted_labels_dict.values()), color='blue')
    plt.bar_label(bars)
    plt.title(f"{predicted_pch} Labels")
    plt.tick_params(labelbottom=False, labeltop=True)
    plt.gca().invert_yaxis()
    

    # Save the report to a file
    plt.tight_layout()
    plt.savefig(eval_report_path)
    plt.close()

"""
    Initial emotion compared to SPCL output matrix 
"""
def initial_to_spcl_matrix(report_path: str, eval_report_path: str):
    file_count = len(os.listdir(os.path.dirname(report_path))) - 1  # Exclude the CSV file itself
    # Read the CSV file from report_path
    with open(report_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        initial_labels = []
        spcl_labels = []
        total = 0
        correct = 0
        with alive_bar(file_count, title="Processing") as bar:
            for row in reader:
                bar()
                total += 1
                initial_labels.append(row["initial_emo"])
                spcl_labels.append(row["emo"])
                if row["initial_emo"] == row["emo"]:
                    correct += 1
        accuracy = correct / total
    print(f"Initial to SPCL accuracy: {accuracy:.2f}")
    plot_matrix(initial_labels, spcl_labels, eval_report_path, "Initial", "SPCL")

def spcl_to_eval_matrix(report_path: str, eval_report_path: str):
    file_count = len(os.listdir(os.path.dirname(report_path))) - 1  # Exclude the CSV file itself
    # Read the CSV file from report_path
    with open(report_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        spcl_labels = []
        eval_labels = []
        total = 0
        correct = 0
        with alive_bar(file_count, title="Processing") as bar:
            for row in reader:
                bar()
                total += 1
                out_prob, score, index, text_lab = classifier.classify_file(
                    row["output_wav"]
                )
                spcl_labels.append(row["emo"])
                eval_labels.append(text_lab[0])
                if text_lab[0] == row["emo"]:
                    correct += 1
        accuracy = correct / total
    print(f"SPCL to eval accuracy: {accuracy:.2f}")
    plot_matrix(spcl_labels, eval_labels, eval_report_path, "SPCL", "Eval")

def initial_to_eval_matrix(report_path: str, eval_report_path: str):
    run_speechbrain(report_path, eval_report_path)


if __name__ == "__main__":
    report_path = "/Users/elnuralimirzayev/Thesis/notebooks/eahris/baselines/benchmark/tts_output/20250908_022659/feed.csv"
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    eval_report_path = f"/Users/elnuralimirzayev/Thesis/notebooks/eahris/reports/report_{timestamp}"
    if not os.path.exists(eval_report_path):
        os.makedirs(eval_report_path)
    initial_to_spcl_matrix(report_path, os.path.join(eval_report_path, "initial_to_spcl.png"))
    spcl_to_eval_matrix(report_path, os.path.join(eval_report_path, "spcl_to_eval.png"))
    initial_to_eval_matrix(report_path, os.path.join(eval_report_path, "initial_to_eval.png"))
