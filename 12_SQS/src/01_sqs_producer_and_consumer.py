import boto3
import json
import time

# Initialize the SQS client
sqs_client = boto3.client('sqs', region_name='ap-southeast-2')
queue_url = 'https://sqs.ap-southeast-2.amazonaws.com/819439780701/DemoSQSQueue'

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

""""
sample output 
python 01_sqs_producer_and_consumer.py
📤 Producer: Sending Order ORD-9981 to SQS...
✅ Message sent! MessageId: 856ae965-c307-4df2-9937-497a6532231f

📥 Consumer: Polling SQS for new messages...
⚙️  Processing Order ORD-9981 for Alice Smith...
🗑️  Order ORD-9981 processed and deleted from queue."""