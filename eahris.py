import configparser
from alive_progress import alive_bar
from llm.openai import OpenaiApi
from spcl.spcl import spcl_run
from baselines import tts_client
from playsound import playsound
from baselines.user.api import start_backend
from baselines.benchmark.benchmark_baseline import benchmark_baseline

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config

def initialize_modules(config, is_benchmark_baseline=False):
    if not is_benchmark_baseline:
        apikey = config["secrets"]["OpenAiApiKey"]
        llm_client = OpenaiApi(api_key=apikey)
    else:
        llm_client = None
    spcl_client = spcl_run
    eatts_client = tts_client
    return llm_client, spcl_client, eatts_client

def user_baseline(spcl_client, eatts_client, llm_client):
    start_backend(spcl_client, eatts_client, llm_client)
    # chat_history = []
    # emo_history = []
    # print("Welcome to the Emotion-Aware Human-Robot Interaction System (EAHRIS)!")
    # while True:
    #     user_input = input()
    #     emo_history = add_to_chathistory(user_input, "User", chat_history, spcl_client)
    #     llm_response = llm_client.chat(user_input, chat_history)
    #     emo_history = add_to_chathistory(llm_response.output_text, "NICO", chat_history, spcl_client)
    #     print(llm_response.output_text)
    #     eatts_client.call_tts_user(llm_response.output_text, emo_history[-1])
    #     wait_for_tts_finish(eatts_client)
    #     print("Message arrived, playing sound...")


def main():
    config = load_config()
    is_benchmark_baseline = config.getboolean("baseline", "IsBenchmarkBaseline", fallback=False)
    llm_client, spcl_client, eatts_client = initialize_modules(config, is_benchmark_baseline)
    if is_benchmark_baseline:
        benchmark_baseline(spcl_client, eatts_client)
    else:
        user_baseline(spcl_client, eatts_client, llm_client)

if __name__ == "__main__":
    main()
