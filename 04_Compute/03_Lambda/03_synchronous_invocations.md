# AWS Lambda: Synchronous Invocations

When working with AWS Lambda, understanding *how* a function is invoked is just as critical as understanding the code inside it. The invocation type dictates how errors are handled, how retries work, and how the response is routed.

The most straightforward method is a **Synchronous Invocation**.

---

## 1. What is a Synchronous Invocation?

A synchronous invocation is a "blocking" call. When a client triggers the Lambda function, it holds the connection open and **waits** for the function to finish executing and return a response (or an error).

**The Golden Rule of Synchronous Invocations:**

* **No Automatic Retries:** If the Lambda function crashes, times out, or throws an exception, AWS does *not* automatically retry the execution. The error is returned directly to the client.
* **Client Responsibility:** It is entirely up to the client application (e.g., your Python script, or the user's web browser) to catch that error and decide what to do next—whether that means surfacing an error message to the user, or implementing an exponential backoff strategy to try the request again.

---

## 2. Which Services Invoke Lambda Synchronously?

Whenever a service requires an immediate response to continue its own workflow, it invokes Lambda synchronously. You must memorize these for the exam:

* **User Invoked:**
* **AWS CLI / SDKs** (when explicitly requesting a response).
* **Elastic Load Balancing (Application Load Balancer):** The ALB waits for the Lambda function to generate the HTML or JSON response to return to the web client.
* **Amazon API Gateway:** The classic REST API pattern. The API Gateway holds the HTTP connection open until Lambda finishes processing the backend logic.
* **Amazon CloudFront (Lambda@Edge):** The CDN waits for your function to modify the HTTP request/response headers before serving the file to the user.


* **Other Synchronous Services:**
* **Amazon Cognito:** e.g., triggering a Lambda function to validate a user's password before allowing them to log in.
* **AWS Step Functions:** Waiting for a task to complete before moving to the next step in the state machine.
* **Amazon Lex / Alexa:** Waiting for the backend logic to determine what the chatbot should say next.
* **Amazon Kinesis Data Firehose:** Waiting for Lambda to transform a batch of records before writing them to S3.



---

## 3. Hands-On: Synchronous Invocation via AWS CLI

If you want to test a synchronous invocation without building an entire API Gateway, you can use the AWS CLI.

Notice how the command structure explicitly captures the output into a file. Because it is synchronous, your terminal will "hang" for a moment while the function runs, and then the results will be written to `response.json`.

```bash
# Using AWS CLI v2
aws lambda invoke \
  --function-name demo-lambda \
  --cli-binary-format raw-in-base64-out \
  --payload '{"key1": "value1"}' \
  --region eu-west-1 \
  response.json

```

*(Note: If the function crashes, the CLI will still exit successfully, but the `response.json` file will contain the stack trace or error message, proving that the client receives the error directly).*

---

## 4. Boto3 Implementation: Synchronous Invocation

When building backend systems or automated scripts, you will frequently invoke Lambda functions synchronously using Python.

The critical parameter here is `InvocationType='RequestResponse'`, which explicitly tells AWS to hold the connection open and wait for the result.

```python
import boto3
import json
from botocore.exceptions import ClientError

# Initialize the Lambda client
lambda_client = boto3.client('lambda', region_name='eu-west-1')
function_name = 'demo-lambda'

def invoke_sync_lambda(payload_dict: dict):
    print(f"🚀 Synchronously invoking '{function_name}'...")
    
    try:
        # The 'RequestResponse' type is what makes this a Synchronous invocation
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse', 
            Payload=json.dumps(payload_dict)
        )
        
        # Check if Lambda returned a handled error (e.g., Python threw an exception)
        if 'FunctionError' in response:
            error_payload = json.loads(response['Payload'].read().decode("utf-8"))
            print(f"❌ Lambda executed but crashed (Client must handle this!): {error_payload}")
            # Here, the developer would write custom retry logic or exponential backoff
            return None
            
        # Success path
        success_payload = json.loads(response['Payload'].read().decode("utf-8"))
        print(f"✅ Success! Lambda returned: {success_payload}")
        return success_payload

    except ClientError as e:
        print(f"❌ AWS API Error (Network/Permissions): {e.response['Error']['Message']}")
        return None

if __name__ == "__main__":
    # Simulate a payload that the Lambda function expects
    test_event = {
        "key1": "value1",
        "key2": "value2"
    }
    
    invoke_sync_lambda(test_event)

```

---

## Interview Preparation: Synchronous vs. Asynchronous

### Summary

Expect questions testing your understanding of *who* is responsible for retries when a function fails, and which AWS services rely on synchronous responses to function correctly.

### Q&A Details

**Q1: A mobile application makes a REST API call to Amazon API Gateway, which triggers a backend AWS Lambda function. Due to a sudden spike in database latency, the Lambda function times out after 10 seconds. Will AWS automatically retry the Lambda function to complete the user's request?**
**Answer:** No. API Gateway invokes Lambda **synchronously**. In a synchronous invocation, AWS does not perform automatic retries. The timeout error (typically a 502 or 504 status code) is returned immediately through API Gateway to the mobile application. The client-side code in the mobile app is responsible for catching the error and initiating a retry.

**Q2: We are architecting a login flow using Amazon Cognito. Before a user is authenticated, we want to trigger a Lambda function to check their IP address against a third-party threat database. Should this Lambda function be invoked synchronously or asynchronously?**
**Answer:** It must be invoked **synchronously**. Amazon Cognito needs to wait for the exact result of the Lambda function (e.g., 'Allow' or 'Deny') before it can proceed with authenticating the user. If it were invoked asynchronously, Cognito would log the user in without waiting for the security check to finish.

**Q3: A developer runs the `aws lambda invoke` command from their terminal to trigger a data-processing script. The script takes 20 seconds to run. The developer notices their terminal freezes and becomes unusable during those 20 seconds. Why does this happen, and how can they prevent it?**
**Answer:** The terminal freezes because the CLI defaults to a **synchronous** invocation (`RequestResponse`), meaning it holds the connection open waiting for the payload return. To prevent the terminal from freezing, the developer should append the parameter `--invocation-type Event` to the command, which changes it to an asynchronous invocation. The CLI will then immediately return a 202 Accepted status and free up the terminal, while the function runs in the background.