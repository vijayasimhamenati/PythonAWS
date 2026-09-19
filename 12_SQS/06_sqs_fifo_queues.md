# AWS SQS FIFO Queues: Strict Ordering & Exactly-Once Delivery

While standard SQS queues are excellent for scaling horizontally, their "Best-Effort Ordering" and "At-Least-Once Delivery" guarantees are insufficient for specific workloads.

If you are processing financial transactions, database state changes, or inventory updates, the order of messages is critical. If a user deposits $10 and then withdraws $10, processing those messages in the reverse order will crash the account balance below zero.

For these strict workloads, you must use **SQS FIFO (First-In-First-Out) Queues**.

---

## 1. Key Characteristics of FIFO Queues

To create a FIFO queue, you must append `.fifo` to the end of the queue name (e.g., `FinancialTransactions.fifo`).

- **Strict Ordering:** Messages are received by the consumer in the exact order they were sent by the producer (1, 2, 3, 4).
- **Exactly-Once Processing:** FIFO queues automatically remove duplicates.
- **Throughput Limits:** Because SQS has to work much harder to guarantee order and remove duplicates, throughput is artificially limited compared to Standard queues.
- 300 messages per second (without batching).
- 3,000 messages per second (with batching).

---

## 2. Deduplication (Exactly-Once Delivery)

If a producer experiences a network hiccup and accidentally sends the same "Process Order #1234" message twice within a **5-minute window**, SQS FIFO will silently drop the second message.

You control how SQS identifies duplicates using two methods:

### A. Content-Based Deduplication (Automatic)

When enabled, SQS automatically generates a SHA-256 hash of the entire message payload. If a second message arrives with the exact same payload (and thus the exact same hash), it is rejected as a duplicate.

### B. MessageDeduplicationId (Explicit)

If your payload contains dynamic timestamps (e.g., `{"order": "1234", "timestamp": "10:01:05"}` and `{"order": "1234", "timestamp": "10:01:07"}`), Content-Based Deduplication will fail because the payloads are slightly different.
Instead, your code explicitly provides a `MessageDeduplicationId` (e.g., the unique transaction ID `tx-1234`) when calling the `SendMessage` API. SQS ignores the payload differences and relies solely on your explicit ID to filter duplicates.

---

## 3. Message Group IDs (Parallel Processing in FIFO)

Strict ordering creates a performance bottleneck. If you have 10 consumers polling a FIFO queue, but strict ordering requires Message 1 to be fully processed and deleted before Message 2 can be touched, you essentially degrade your system to a single active consumer at any given time.

**The Solution: MessageGroupIds**
When sending a message to a FIFO queue, you _must_ provide a `MessageGroupId`.

- **The Rule:** SQS only guarantees strict ordering for messages _within the same group_.

### How it enables scale:

Imagine an e-commerce platform processing orders for thousands of different users.

- You don't care if User A's order is processed before User B's order.
- You _only_ care that User A's "Add to Cart" is processed before User A's "Checkout".

If you use the Customer ID as the `MessageGroupId`, SQS creates parallel "lanes" within the queue.
Consumer 1 can process User A's messages in strict order, while Consumer 2 simultaneously processes User B's messages in strict order. This restores horizontal scalability to your backend while maintaining strict logical ordering where it actually matters.

---

## 4. Practical Guide: Boto3 Implementation for FIFO

Here is how you interact with a FIFO queue using Python, specifically highlighting the mandatory `MessageGroupId` and the explicit `MessageDeduplicationId`.

```python
import boto3
import uuid

# Initialize SQS client
sqs_client = boto3.client('sqs', region_name='us-east-1')
# Note the required .fifo suffix
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/FinancialTransactions.fifo'

def send_financial_transaction(user_id: str, action: str, amount: float, transaction_id: str):
    print(f"📤 Sending Transaction: {action} ${amount} for User {user_id}")

    # We use the unique transaction ID to guarantee Exactly-Once delivery.
    # If the network fails and we retry this function, SQS will drop the duplicate.
    dedup_id = transaction_id

    # We use the User ID as the Group ID.
    # This guarantees all transactions for THIS user are processed in strict order,
    # while allowing other users' transactions to be processed in parallel.
    group_id = user_id

    payload = f"Action: {action}, Amount: {amount}"

    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=payload,
        MessageDeduplicationId=dedup_id,
        MessageGroupId=group_id
    )

    print(f"✅ Sent. MessageId: {response['MessageId']}")

if __name__ == "__main__":
    # Simulate a user performing sequenced financial actions

    # Generate a unique ID for the deposit
    tx_1 = str(uuid.uuid4())
    send_financial_transaction(user_id="user-99", action="Deposit", amount=100.0, transaction_id=tx_1)

    # Generate a unique ID for the withdrawal
    tx_2 = str(uuid.uuid4())
    send_financial_transaction(user_id="user-99", action="Withdraw", amount=20.0, transaction_id=tx_2)

    # Simulate a network retry accidentally sending the exact same deposit again
    print("\n⚠️ Simulating network retry (sending duplicate deposit)...")
    send_financial_transaction(user_id="user-99", action="Deposit", amount=100.0, transaction_id=tx_1)
    print("🔒 SQS FIFO silently dropped the duplicate at the server level.")

```

---

## Interview Preparation: SQS Standard vs. FIFO

### Summary

Exams will constantly test your ability to choose between Standard and FIFO based on throughput requirements versus ordering guarantees.

### Q&A Details

**Q1: An application processes 5,000 IoT sensor readings per second. The engineering team wants to decouple the ingestion layer from the database processing layer. Which SQS queue type should they use?**
**Answer:** They must use a **Standard SQS Queue**. A FIFO queue has a hard limit of 3,000 messages per second (even with batching). Standard queues offer unlimited throughput, which is required for the 5,000 messages per second payload.

**Q2: An e-commerce platform processes user shopping carts. If a user clicks 'Add Item' and then immediately clicks 'Remove Item', the backend must process the 'Add' before the 'Remove'. The current architecture uses a Standard SQS Queue, but occasionally users are receiving errors because the 'Remove' action is processed first. How do you fix this?**
**Answer:** Standard SQS queues only provide "Best-Effort Ordering." To guarantee strict sequential processing, the architecture must be migrated to an **SQS FIFO Queue**. The developer must append `.fifo` to the queue name and update the application code to include a `MessageGroupId` (such as the user's Session ID) when publishing messages.

**Q3: We have an SQS FIFO Queue configured without Content-Based Deduplication. A producer sends a message, but the consumer crashes before processing it. The visibility timeout expires, and the message goes back into the queue. Will the deduplication feature prevent a new consumer from pulling this message?**
**Answer:** No. Deduplication in SQS FIFO specifically prevents a _Producer_ from injecting the same message into the queue twice within a 5-minute window. It has absolutely no effect on a _Consumer_ pulling an existing message multiple times due to a visibility timeout expiration.
