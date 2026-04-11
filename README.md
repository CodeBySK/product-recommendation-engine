# 🛒 Real-Time Product Recommendation Engine

A production-grade retail streaming pipeline built with **Apache Kafka**, **Apache Spark**, and **Machine Learning** that intelligently handles out-of-stock scenarios by recommending alternatives to customers in real time — instead of simply cancelling their order.

---

## 🎯 The Problem This Solves

Traditional e-commerce: Customer places order → SKU is out of stock → Order cancelled → Customer frustrated.

**This system**: Customer places order → SKU is out of stock → Pipeline automatically finds:
1. Same SKU available at a nearby store for pickup
2. A similar product (via ML similarity) that is in stock
3. Only cancels if truly no alternative exists

---

## 🏗️ Architecture

```
Customer Places Order
        │
        ▼
┌───────────────────┐
│   orders-topic    │  (Kafka)
└────────┬──────────┘
         │
         ▼
┌─────────────────────┐
│  Fulfilment Checker │  (Spark Streaming - Job 1)
│  checks Redis stock │
└──────────┬──────────┘
           │
     ┌─────┴──────┐
     │            │
  In Stock    Out of Stock
     │            │
     ▼            ▼
┌─────────┐  ┌──────────────────┐
│ fulfil  │  │ dead-letter-topic│  (Circuit Breaker)
│ -topic  │  └────────┬─────────┘
└─────────┘           │
                      ▼
           ┌─────────────────────┐
           │ Recommendation      │  (Spark ML - Job 2)
           │ Engine              │
           └──────────┬──────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
     Nearby        Similar     Cancel
     Store         Product     Order
     Pickup        (ML)
          │           │           │
          └───────────┴───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │  notification-topic   │
          │  → Customer Notified  │
          └───────────────────────┘
```

---

## 🧰 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Message Broker | Apache Kafka | Event streaming backbone |
| Stream Processing | Apache Spark (via PySpark) | Real-time job processing |
| ML / Similarity | sentence-transformers, scikit-learn | Product recommendation |
| Fast Cache | Redis | Real-time inventory lookup |
| Database | PostgreSQL | Store inventory, product catalog |
| ML Tracking | MLflow | Model versioning & experiments |
| Notebooks | JupyterLab + PySpark | Development & exploration |
| Orchestration | Docker Compose | Local environment management |

---

## 📦 Kafka Topics

| Topic | Description |
|---|---|
| `orders-topic` | All incoming customer orders |
| `fulfil-topic` | Orders where SKU is in stock → proceed |
| `dead-letter-topic` | Orders where SKU is out of stock → circuit breaker |
| `notification-topic` | Recommendation results sent to customer |
| `feedback-topic` | Customer response to recommendation (accepted/rejected) |

---

## 🚀 Local Setup

### Prerequisites

| Tool | Purpose |
|---|---|
| Docker Desktop | Runs all services |
| Python 3.10+ | Local scripting |
| VS Code | Code editor |

### Project Structure

```
product-recommendation-project/
├── docker-compose.yml
├── db/
│   └── init.sql                  # PostgreSQL schema
├── notebooks/
│   └── exploration.ipynb         # Jupyter notebooks
├── spark-jobs/
│   ├── fulfilment_checker.py     # Spark Job 1
│   └── recommendation_engine.py  # Spark Job 2
├── producers/
│   └── order_producer.py         # Simulates customer orders
└── ml/
    ├── train_embeddings.py       # Product similarity model
    └── model/                    # Saved model artifacts
```

### Start the Stack

```bash
# 1. Create required folders
mkdir -p db notebooks spark-jobs producers ml
touch db/init.sql

# 2. Start all services
docker-compose up -d

# 3. Verify all containers are running
docker-compose ps
```

### Service URLs

| Service | URL | Notes |
|---|---|---|
| JupyterLab | http://localhost:8888 | Main development environment |
| Kafka UI | http://localhost:8081 | Monitor topics and messages |
| Spark UI | http://localhost:4040 | Active when a Spark job runs |
| MLflow | http://localhost:5001 | Model tracking and registry |
| PostgreSQL | localhost:5432 | DB: retail / User: admin |
| Redis | localhost:6379 | Inventory cache |

### Kafka Connection

| From | Bootstrap Server |
|---|---|
| Inside Docker (Jupyter) | `kafka:29092` |
| Outside Docker (Mac terminal) | `localhost:9092` |

---

## 📋 Getting Started — Step by Step

### Step 1 — Install Dependencies (in Jupyter)

```python
import subprocess
subprocess.run(['pip', 'install', 'kafka-python-ng', 'redis',
                'psycopg2-binary', 'sentence-transformers',
                'scikit-learn', 'mlflow', 'faker', '--quiet'])
```

### Step 2 — Create Kafka Topics

```python
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
```

### Step 3 — Seed Inventory into Redis

```python
import redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)

for i in range(1, 41):
    r.set(f"stock:P-{i}", 100)   # P-1 to P-40: IN STOCK

for i in range(41, 51):
    r.set(f"stock:P-{i}", 0)     # P-41 to P-50: OUT OF STOCK → triggers DLT

print("✅ Inventory seeded!")
```

### Step 4 — Produce Test Orders

```python
from kafka import KafkaProducer
import json, time, random

producer = KafkaProducer(
    bootstrap_servers='kafka:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',
    retries=3
)

for _ in range(10):
    order = {
        "orderId":    f"ORD-{random.randint(1000, 9999)}",
        "customerId": f"C-{random.randint(1, 100)}",
        "productId":  f"P-{random.randint(1, 50)}",  # P-41 to P-50 will hit DLT
        "quantity":   random.randint(1, 5),
        "price":      round(random.uniform(10, 200), 2),
        "timestamp":  time.time(),
        "status":     "PENDING"
    }
    producer.send("orders-topic", order)
    print(order)
    time.sleep(1)

producer.flush()
print("✅ All orders sent!")
```

### Step 5 — Start Spark Session

```python
from pyspark.sql import SparkSession

spark = (SparkSession.builder
    .master("local[*]")
    .appName("RetailStreaming")
    .getOrCreate())

print(f"✅ Spark version: {spark.version}")
```


---

## 👷 Responsibilities by Role

### As a Data Engineer
- Kafka topic design, partitioning, retention
- Spark Streaming jobs (Job 1 + Job 2 routing)
- Dead Letter Queue pattern and circuit breaker
- Redis and PostgreSQL integration
- Pipeline monitoring and observability

### As an ML Engineer
- Product embedding model (sentence-transformers)
- Cosine similarity recommendation algorithm
- Geo-lookup for nearby store availability
- MLflow model tracking and versioning
- Feedback loop and automated retraining

---

## 🐛 Common Issues & Fixes

| Error | Cause | Fix |
|---|---|---|
| `NoBrokersAvailable` | Wrong bootstrap server | Use `kafka:29092` inside Docker, `localhost:9092` outside |
| `bitnami/spark not found` | Bitnami removed from Docker Hub Aug 2025 | Use `jupyter/pyspark-notebook` which has Spark built in |
| Port 5000 in use | macOS AirPlay Receiver | MLflow mapped to port 5001 |
| Port 8080 in use | Airflow | Kafka UI mapped to port 8081 |
| Jupyter token prompt | Default security | Set `JUPYTER_TOKEN: ""` in docker-compose |

---

## 📚 Learning Resources

| Topic | Resource |
|---|---|
| Kafka | https://kafka.apache.org/documentation |
| Spark Structured Streaming | https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html |
| sentence-transformers | https://www.sbert.net |
| MLflow | https://mlflow.org/docs/latest/index.html |
| Dead Letter Queue Pattern | https://www.confluent.io/blog/dead-letter-queue-kafka |

---

## 💡 Key Design Patterns Used

- **Circuit Breaker** — DLT prevents order cancellation without attempting recovery
- **Event-Driven Architecture** — every state change is a Kafka event
- **CQRS** — separate read (Redis) and write (PostgreSQL) paths for inventory
- **Feedback Loop** — customer responses retrain the recommendation model over time

---