from kafka.admin import KafkaAdminClient, NewTopic

admin = KafkaAdminClient(
    bootstrap_servers="umbrel.local:9092",
    client_id="topic-manager"
)

existing_topics = admin.list_topics()

topics = [
    ("orders-topic", 3),
    ("dead-letter-topic", 3),
    ("fulfil-topic", 3),
    ("notification-topic", 3),
    ("feedback-topic", 3),
]

new_topics = [
    NewTopic(name, num_partitions=p, replication_factor=1)
    for name, p in topics
    if name not in existing_topics
]

if new_topics:
    admin.create_topics(new_topics=new_topics)
    print("✅ Topics created:", [t.name for t in new_topics])
else:
    print("⚠️ Topics already exist")