from kafka.admin import KafkaAdminClient, NewTopic

admin = KafkaAdminClient(bootstrap_servers='kafka:29092')

topics = [
    NewTopic('orders-topic',       num_partitions=3, replication_factor=1),
    NewTopic('dead-letter-topic',  num_partitions=3, replication_factor=1),
    NewTopic('fulfil-topic',       num_partitions=3, replication_factor=1),
    NewTopic('notification-topic', num_partitions=3, replication_factor=1),
    NewTopic('feedback-topic',     num_partitions=3, replication_factor=1),
]

admin.create_topics(new_topics=topics)
print("✅ All topics created!")
