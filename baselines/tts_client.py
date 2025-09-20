import pika
import json

parameters = pika.ConnectionParameters(host='localhost', port=5672)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Function to ensure the channel is open
def ensure_channel():
    global connection, channel
    if channel.is_closed:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

# emo: [neu], [hap], [ang], [sad]
def call_tts_benchmark(msg):
    ensure_channel()
    payload = {
        "messages": msg,
        "baseline": "benchmark"
    }
    payload_json = json.dumps(payload)
    channel.basic_publish(exchange='tts_input_exchange', routing_key='input', body=payload_json)

def call_tts_user(msg, emo):
    ensure_channel()
    payload = {
        "text": msg,
        "emo": emo,
        "baseline": "user"
    }
    message_json = json.dumps(payload)
    channel.basic_publish(exchange='tts_input_exchange', routing_key='input', body=message_json)

def wait_for_finish(callback):
    ensure_channel()
    channel.basic_consume(queue='tts_output', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
