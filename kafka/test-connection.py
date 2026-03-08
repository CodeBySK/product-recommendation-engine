from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'orders-topic',
    bootstrap_servers='localhost:9092'
)

print("Connected!")