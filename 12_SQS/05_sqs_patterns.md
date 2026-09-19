# Advanced SQS Developer Patterns & API Reference

As you build production-grade applications that integrate with Amazon SQS, you must move beyond basic message sending and receiving. Optimizing API call costs, handling large payloads, and managing message lifecycles programmatically are core requirements for both system architecture and certification exams.

---

## 1. Long Polling vs. Short Polling

When a consumer checks an SQS queue for messages, it sends a `ReceiveMessage` API call. How the queue responds depends on whether **Long Polling** or **Short Polling** is enabled.

### Short Polling (Default)

- The consumer asks the queue for messages.
- If the queue is empty, SQS immediately returns an empty response.
- **The Problem:** If your application polls an empty queue continuously using short polling, you will flood AWS with millions of empty API requests. This burns CPU cycles, increases network latency, and significantly racks up unnecessary API costs.

### Long Polling (Best Practice)

- The consumer asks the queue for messages and specifies a wait time (up to **20 seconds**).
- If the queue is empty, SQS **holds the connection open** for up to 20 seconds, waiting for a message to arrive.
- If a message is dropped into the queue during that window, SQS immediately pushes it to the consumer.
- **The Benefits:**

1. **Lower Cost:** Dramatically reduces the number of empty API responses (you only pay per API request when a message is returned or a long poll times out).
2. **Lower Latency:** Messages are delivered instantly the moment they hit the queue because the consumer's connection is already open and waiting.

**How to Enable Long Polling:**

- **Queue-Level:** Set the **Receive Message Wait Time** to 20 seconds in the AWS Console or via CloudFormation.
- **API-Level:** Set the `ReceiveMessageWaitTimeSeconds` parameter in your code when calling `receive_message()`.

---

## 2. Handling Large Payloads: The SQS Extended Client

Amazon SQS has a strict hard limit: **Maximum message size is 256 KB**.

What happens if you need to pass a 500 MB video file, a massive genomic dataset, or a multi-megabyte database dump through a queue? You cannot put the raw data directly into SQS.

**The Solution: The SQS Extended Client Library**
Instead of sending the large payload through SQS, you use the Extended Client pattern (supported via official AWS client libraries):

1. **Upload to S3:** The producer uploads the large file (e.g., a video) directly into an **Amazon S3 bucket**.
2. **Send Pointer:** The producer sends a small metadata message into the SQS queue. This message contains a **pointer (URI/reference)** to the file's location in S3.
3. **Consume & Download:** The consumer pulls the small metadata message from SQS, reads the S3 pointer, and fetches the large file directly out of S3 for processing.

---

## 3. Essential SQS API Reference for Developers

You should be familiar with the core API actions and parameters tested on the exam:

| API Action                    | Purpose                                                                     | Key Parameters / Notes                                                            |
| ----------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **`CreateQueue`**             | Provisions a new queue.                                                     | `MessageRetentionPeriod`, `VisibilityTimeout`.                                    |
| **`DeleteQueue`**             | Deletes a queue and all its messages.                                       | Irreversible.                                                                     |
| **`PurgeQueue`**              | Clears all messages from a queue instantly.                                 | Useful in dev environments.                                                       |
| **`SendMessage`**             | Publishes a message to the queue.                                           | `DelaySeconds` (up to 15 mins), `MessageBody`.                                    |
| **`ReceiveMessage`**          | Polls the queue for messages.                                               | `MaxNumberOfMessages` (up to 10), `ReceiveMessageWaitTimeSeconds` (Long Polling). |
| **`DeleteMessage`**           | Removes a processed message from the queue.                                 | Requires the unique `ReceiptHandle` returned during `ReceiveMessage`.             |
| **`ChangeMessageVisibility`** | Extends or shortens the visibility timeout for a specific message inflight. | Prevents duplicate processing during long-running tasks.                          |

### Cost Optimization: Batch APIs

To reduce API costs and network overhead, SQS supports batch operations:

- `SendMessageBatch` (up to 10 messages at once)
- `DeleteMessageBatch` (up to 10 messages at once)
- `ChangeMessageVisibilityBatch` (up to 10 messages at once)

---

## 4. Practical Guide: Configuring Long Polling in Boto3

Here is how you programmatically configure long polling using `boto3` when polling a queue.

```python
import boto3

sqs_client = boto3.client('sqs', region_name='us-east-1')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/DemoQueue'

def poll_queue_with_long_polling():
    print("📥 Polling queue with 20-second Long Polling enabled...")

    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=5,
        # Enabling Long Polling at the API level (waits up to 20 seconds for messages)
        ReceiveMessageWaitTimeSeconds=20
    )

    messages = response.get('Messages', [])
    if not messages:
        print("📭 Long poll timed out after 20 seconds. No messages arrived.")
        return

    for msg in messages:
        print(f"✅ Received message: {msg['Body']}")

        # Clean up / delete message after processing
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg['ReceiptHash'] if 'ReceiptHash' in msg else msg['ReceiptHandle']
        )

if __name__ == "__main__":
    poll_queue_with_long_polling()

```

---

## Interview Preparation: Advanced SQS

### Summary

Interviews and exams frequently test your ability to optimize SQS cost and performance using Long Polling, and your architecture pattern choices for handling payloads exceeding 256 KB.

### Q&A Details

**Q1: An enterprise application processes high volumes of financial transactions using SQS. The CloudWatch metrics show an extremely high number of `NumberOfEmptyReceives` API requests, which is driving up AWS bills and wasting compute cycles. How can this be optimized?**
**Answer:** The consumers are currently using Short Polling. You should enable **Long Polling** by setting `ReceiveMessageWaitTimeSeconds` to 20 seconds (either at the queue level or in the API request). This forces the consumer to hold the connection open for up to 20 seconds waiting for messages, drastically reducing empty API calls, lowering costs, and improving throughput latency.

**Q2: Your team needs to build a video-processing pipeline where user uploads average 200 MB in size. A junior developer suggests pushing the raw binary video data directly into a standard SQS queue. Why will this fail, and what architectural pattern should be used instead?**
**Answer:** This will fail because standard SQS queues have a strict maximum message size limit of **256 KB**. Attempting to push a 200 MB file directly will result in an API validation error. Instead, you should implement the **SQS Extended Client** pattern: upload the video file into an **Amazon S3 bucket**, and push a lightweight metadata message containing the S3 pointer reference into the SQS queue for the backend workers to process.

**Q3: A consumer worker pulls a message from an SQS queue and begins running a complex script that takes 45 seconds. The queue's default visibility timeout is set to 30 seconds. What will happen before the script finishes executing, and how can you fix it in code?**
**Answer:** Because the processing time exceeds the 30-second visibility timeout, SQS will assume the worker crashed and make the message visible in the queue again. Another worker will pull the same message, resulting in duplicate processing. To fix this, your worker code should periodically invoke the **`ChangeMessageVisibility`** API during execution to explicitly request more time before the timeout expires.
