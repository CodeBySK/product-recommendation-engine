from kafka import KafkaProducer
import json, time, random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
i = 5
while i:
    order = {
            "orderId":    f"ORD-{random.randint(1000,9999)}",
            "customerId": f"C-{random.randint(1,100)}",
            "productId":  f"P-{random.randint(1,50)}",
            "quantity":   random.randint(1, 5),
            "price":      round(random.uniform(10, 200), 2),
            "timestamp":  time.time(),       # ← needed for Spark watermarking
            "status":     "PENDING"          # ← will change to FULFILLED or DLT
    }
    i -= 1

    producer.send("orders-topic", order)
    print(order)
    time.sleep(1)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',              # ← wait for broker confirmation
    retries=3                # ← retry on failure
)

# After your loop, always flush to ensure all messages are sent
producer.flush()
print("✅ All messages delivered to Kafka!")