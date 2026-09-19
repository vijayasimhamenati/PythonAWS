# Practical Guide: Provisioning and Interacting with SQS

In this hands-on lab, we will use the AWS Management Console to create a Standard SQS queue, act as a producer by sending messages into it, and act as a consumer by pulling and deleting those messages.

---

## 1. Creating the Standard Queue

1. Navigate to the **Amazon SQS** dashboard in the AWS Console.
2. Click **Create queue**.
3. **Type:** Select **Standard**. (We will cover FIFO—First-In-First-Out—queues in a later lecture).
4. **Name:** `DemoQueue`

### Key Configuration Settings

Scroll down to the **Configuration** section. These are the default values that define how your queue behaves.

- **Visibility timeout (30 seconds):** This is critical. When a consumer pulls a message, the message becomes "invisible" to all other consumers for 30 seconds. If the consumer does not explicitly delete the message within this window, the message will reappear in the queue, causing it to be processed twice.
- **Message retention period (4 Days):** If a message sits in the queue for 4 days without being processed, SQS will automatically delete it.
- **Maximum message size (256 KB):** The absolute limit for a standard SQS payload.

### Encryption Settings

- By default, SQS enables **Server-Side Encryption (SSE)** using an AWS-managed key (`SSE-SQS`). This ensures data is encrypted at rest automatically without you needing to configure AWS KMS. Leave this default selected.

Click **Create queue** at the bottom of the page.

---

## 2. Acting as the Producer (Sending Messages)

Now that the queue exists, let's simulate a web frontend sending data into it.

1. On your `DemoQueue` page, click the **Send and receive messages** button in the top right corner.
2. In the **Message body** text box, type: `Order-1234: Process Shipping`.
3. Click **Send message**.
4. Repeat the process two more times with `Order-5678` and `Order-9999`.

You have just acted as an upstream producer. The messages are now sitting safely in the buffer.

---

## 3. Acting as the Consumer (Polling & Processing)

Now, let's simulate the backend worker tier.

1. Scroll down to the **Receive messages** section on the same page.
2. You will see `Messages available: 3`.
3. Click **Poll for messages**.
4. The console will reach out to the queue and pull the messages down. You will see them appear in the list below.

### The Visibility Timeout in Action

1. Click on one of the messages to view its details (you can see your original text in the Body).
2. **Wait 30 seconds.**
3. Do not delete the message. Instead, click **Poll for messages** again.
4. Look at the **Receive count** column. It has increased! Because you did not delete the message within the 30-second visibility timeout, SQS assumed your consumer crashed, and it put the message back into the queue for someone else to process.

This is why SQS guarantees **At-Least-Once Delivery**.

### Processing and Deletion

To properly complete the lifecycle:

1. Select all the messages in the list using the checkboxes.
2. Click **Delete**.
3. Confirm the deletion.

You have signaled to SQS that the work is finished. If you click **Poll for messages** again, the queue will be empty.

---

## 4. The Purge Command

If your developers are testing an application and accidentally flood the queue with 10,000 bad messages, you do not need to pull and delete them one by one.

1. In the SQS console, select your `DemoQueue`.
2. Click **Purge**.
3. Type `purge` to confirm.

This is a blunt instrument that instantly wipes the queue completely clean. It is highly useful in Development environments, but should rarely (if ever) be used in Production.

---

## 5. Boto3 Implementation: Visibility Timeout

Here is a `boto3` script demonstrating how a consumer pulls a message, intentionally takes too long to process it, and causes the message to reappear in the queue.

```python
import boto3
import time

# Initialize SQS client
sqs_client = boto3.client('sqs', region_name='us-east-1')
# Replace with your actual Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/DemoQueue'

def process_messages_badly():
    print("📥 Consumer: Polling for messages...")
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        # Setting visibility timeout explicitly for this API call (seconds)
        VisibilityTimeout=5
    )

    messages = response.get('Messages', [])
    if not messages:
        print("📭 Queue is empty.")
        return

    msg = messages[0]
    print(f"⚙️  Processing message. Receive Count: {msg.get('Attributes', {}).get('ApproximateReceiveCount', 1)}")

    # ❌ BAD PRACTICE: The consumer takes 10 seconds to process the file,
    # but the Visibility Timeout was set to 5 seconds.
    print("⏳ Processing... (this will take 10 seconds)")
    time.sleep(10)

    # By the time the code reaches here, SQS has already made the message visible
    # to other consumers again because the 5-second timeout expired.

    print("🗑️  Attempting to delete message...")
    try:
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg['ReceiptHandle']
        )
        print("✅ Message deleted.")
    except Exception as e:
        print(f"❌ Failed to delete. The receipt handle likely expired. Error: {e}")

if __name__ == "__main__":
    # Ensure there is at least one message in the queue before running this
    sqs_client.send_message(QueueUrl=queue_url, MessageBody="Test Payload")

    # Run the bad consumer
    process_messages_badly()

```

### Understanding the Error

If you run this script, it will fail to delete the message. Because the script slept for 10 seconds (exceeding the 5-second visibility timeout), the `ReceiptHandle` expired. SQS put the message back in the queue for someone else.

**The Fix:** If your backend logic (like processing a large video) takes longer than the queue's configured visibility timeout, your consumer must issue a `ChangeMessageVisibility` API call to explicitly ask SQS for more time before the original timeout expires.
