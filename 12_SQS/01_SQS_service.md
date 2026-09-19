# AWS Integration & Messaging: Decoupling with SQS

As your architecture grows from a simple monolithic application into a distributed system of microservices, managing how those services communicate becomes critical.

If Service A talks directly to Service B (Synchronous Communication), and Service B experiences a sudden spike in traffic and crashes, Service A will also fail because it is waiting for a response.

The solution is **Asynchronous Communication** using middleware. Amazon Simple Queue Service (SQS) is the oldest and most foundational middleware service in AWS, designed specifically to **decouple** applications.

---

## 1. Core Mechanics of Amazon SQS

SQS acts as a highly scalable buffer between the component generating data (the Producer) and the component processing data (the Consumer).

- **The Queue:** A temporary holding area for messages. SQS Standard queues offer unlimited throughput and unlimited message capacity.
- **Producers:** Applications (e.g., an EC2 instance hosting a web frontend) that use the `SendMessage` API to push data into the queue.
- **Consumers:** Applications (e.g., EC2 instances, Lambda functions) that use the `ReceiveMessage` API to pull data from the queue.

### The Consumer Lifecycle

1. **Poll:** The consumer asks the queue, "Do you have any messages?"
2. **Receive:** The queue returns up to 10 messages at a time.
3. **Process:** The consumer executes its business logic (e.g., processing a video, inserting a record into RDS).
4. **Delete:** Once processing is successful, the consumer _must_ call the `DeleteMessage` API. If it fails to do this, the message will eventually reappear in the queue and be processed again by another consumer.

---

## 2. Key Characteristics of SQS Standard

You must memorize these default limits and behaviors for the exam:

- **Message Size:** Maximum of **256 KB** . To send larger payloads, you use the SQS Extended Client Library which stores the payload in S3 and sends a reference link in the queue.
- **Retention Period:** Messages are kept in the queue for **4 days** by default, up to a maximum of **14 days**.
- **Delivery Guarantee:** **At-Least-Once Delivery**. Because it is a highly distributed system, SQS may occasionally deliver the same message more than once. Your consumer application must be _idempotent_ (able to handle duplicate messages safely without corrupting data).
- **Ordering:** **Best-Effort Ordering**. SQS Standard does not guarantee that messages will be processed in the exact order they were received. (If strict ordering is required, you must use an SQS FIFO Queue, which we will cover later).

---

## 3. Scaling with SQS and Auto Scaling Groups (ASG)

One of the most powerful and frequently tested architectural patterns in AWS is scaling compute resources based on the length of an SQS queue.

Imagine you have an EC2 Auto Scaling Group acting as your Consumer tier.

1. You monitor the CloudWatch metric **`ApproximateNumberOfMessagesVisible`** (the length of the queue).
2. You set a CloudWatch Alarm: "If there are more than 1,000 messages waiting in the queue, trigger an ASG Scale-Out."
3. The ASG automatically launches more EC2 instances to drain the queue faster.
4. When the queue length drops, another alarm triggers a Scale-In, terminating the instances to save money.

---

## 4. Boto3 Implementation

Here is a Python script demonstrating how to act as both a Producer and a Consumer using the `boto3` SDK.

```python
import boto3
import json
import time

# Initialize the SQS client
sqs_client = boto3.client('sqs', region_name='us-east-1')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/MyDemoQueue'

def produce_message(order_id: str, customer_name: str):
    """Acts as the Frontend Tier sending an order to the queue."""
    message_body = {
        "order_id": order_id,
        "customer": customer_name,
        "action": "process_shipping"
    }

    print(f"📤 Producer: Sending Order {order_id} to SQS...")
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body)
    )
    print(f"✅ Message sent! MessageId: {response['MessageId']}\n")

def consume_messages():
    """Acts as the Backend Tier polling for work."""
    print("📥 Consumer: Polling SQS for new messages...")

    # The 'ReceiveMessage' API call
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10, # Receive up to 10 messages at once
        WaitTimeSeconds=5       # Long Polling (wait up to 5 seconds for a message to arrive)
    )

    messages = response.get('Messages', [])
    if not messages:
        print("📭 Queue is empty. No work to do.")
        return

    for msg in messages:
        # 1. Extract the payload and the Receipt Handle (required for deletion)
        payload = json.loads(msg['Body'])
        receipt_handle = msg['ReceiptHandle']

        # 2. Process the message (Simulated Business Logic)
        print(f"⚙️  Processing Order {payload['order_id']} for {payload['customer']}...")
        time.sleep(2) # Simulating database inserts or backend work

        # 3. CRITICAL: Delete the message from the queue so it isn't processed again
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print(f"🗑️  Order {payload['order_id']} processed and deleted from queue.")

if __name__ == "__main__":
    # Simulate a user placing an order on the website
    produce_message(order_id="ORD-9981", customer_name="Alice Smith")

    # Simulate the backend worker picking up the job
    consume_messages()

```

### Security Note

SQS supports **Encryption in Flight** (via HTTPS APIs) and **Encryption at Rest** (using AWS KMS). Access to the queue is managed via standard IAM Policies, or via **SQS Access Policies** (which are resource-based policies similar to S3 Bucket Policies, allowing cross-account access or allowing other AWS services like SNS to write to the queue).
