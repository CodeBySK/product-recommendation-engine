from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaConsumer
from kafka.errors import TopicAlreadyExistsError, KafkaError


consumer = KafkaConsumer(
    'orders-topic',
    bootstrap_servers='localhost:9092'
)

print("Connected!")

admin = KafkaAdminClient(bootstrap_servers='localhost:9092')

topics = [
    NewTopic('orders-topic',       num_partitions=3, replication_factor=1),
    NewTopic('dead-letter-topic',  num_partitions=3, replication_factor=1),
    NewTopic('fulfil-topic',       num_partitions=3, replication_factor=1),
    NewTopic('notification-topic', num_partitions=3, replication_factor=1),
    NewTopic('feedback-topic',     num_partitions=3, replication_factor=1),
]

try:
    admin.create_topics(new_topics=topics)
    print("✅ Topics created")

except TopicAlreadyExistsError:
    print("⚠️ Topic already exists")
    existing_topics = admin.list_topics()
    print(existing_topics)


except KafkaError as e:
    print(f"Kafka error: {e}")