from confluent_kafka import Producer
import json
import csv
import time
from datetime import datetime
import os

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))



def send_data_to_kafka(bootstrap_servers, topic, data_path):
    print(f'Loading data from {data_path}')
    with open(data_path, 'r') as csv_file:
        data = list(csv.DictReader(csv_file))

        # Initialize producer
        producer = Producer({'bootstrap.servers': bootstrap_servers})

        total_rows = len(data)
        print(f"Total rows to send: {total_rows}")

        for index, row in enumerate(data):
            try:
                # Convert to a datetime object
                dt_object = datetime.fromisoformat(row['Timestamp'])

                # Convert datetime to milliseconds since epoch
                current_timestamp_ms = int(time.time() * 1000)
                row['Timestamp'] = current_timestamp_ms
                row["PowerFlowValue"]=float(row["PowerFlowValue"])
                row["PowerLineID"]=float(row["PowerLineID"])
                payload = json.dumps(row)

                # Produce
                producer.produce(topic=topic, value=payload.encode('utf-8'), callback=delivery_report)
                producer.poll(0)
                time.sleep(5)
            except Exception as e:
                print(f"An error occurred: {e}")

            # Progress bar update and sleep omitted for brevity

        producer.flush()
        print(f"\nFinished sending data from {data_path}")

if __name__ == "__main__":
    BOOTSTRAP_SERVER = 'kafka:9092'  # Replace with your actual bootstrap server
    TOPIC = 'Epsymolo'  # Replace with your actual topic
    DATA_DIR = 'Data'  # Replace with your actual data directory

    # Iterate through all CSV files in the specified directory
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
            file_path = os.path.join(DATA_DIR, filename)
            send_data_to_kafka(BOOTSTRAP_SERVER, TOPIC, file_path)
