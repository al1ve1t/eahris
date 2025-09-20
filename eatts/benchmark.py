import os
import pika
import soundfile as sf
import json
from pika.adapters.blocking_connection import BlockingChannel
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from model import synthesize_msg

def benchmark_baseline(messages):
    for message in messages:
        print(f"Received message: {message}")
        synthesize_msg(message, message["output_wav"])

def callback(ch, method, properties, body):
    try:
        feed = json.loads(body.decode())
        print(f"Received feed: {feed}")
        if feed["baseline"] == "benchmark":
            benchmark_baseline(feed["messages"])
        else:
            synthesize_msg(feed)
        # Send finish signal to tts_output queue
        finish_message = json.dumps({"status": "finished"})
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
        channel = connection.channel()
        channel.basic_publish(exchange='tts_output_exchange', routing_key='output', body=finish_message)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error processing message: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def listen(channel: BlockingChannel):
    channel.exchange_declare(exchange='tts_input_exchange', exchange_type='direct')
    channel.exchange_declare(exchange='tts_output_exchange', exchange_type='direct')
    channel.queue_declare(queue='tts_input')
    channel.queue_declare(queue='tts_output')
    channel.queue_purge(queue='tts_input')
    channel.queue_purge(queue='tts_output')
    channel.queue_bind(exchange='tts_input_exchange', queue='tts_input', routing_key='input')
    channel.queue_bind(exchange='tts_output_exchange', queue='tts_output', routing_key='output')
    channel.basic_consume(queue='tts_input', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def start_server():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
    channel = connection.channel()
    listen(channel)
    