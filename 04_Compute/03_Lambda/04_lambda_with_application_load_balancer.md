# Application Load Balancer (ALB) & AWS Lambda Integration

While AWS Lambda is often triggered by backend events (like S3 uploads or SQS messages), you will frequently need to expose your serverless code to the public internet via HTTP/HTTPS.

You can achieve this by placing an **Application Load Balancer (ALB)** in front of your Lambda function. The ALB acts as the bridge between standard web traffic and the serverless AWS ecosystem.

---

## 1. How the Integration Works (Synchronous)

When a user visits your website, the ALB receives the HTTP request and invokes your Lambda function **synchronously**—meaning the ALB holds the client's HTTP connection open and waits for the Lambda function to finish running and return a response.

Because Lambda speaks JSON (not HTTP), the ALB performs a critical translation step in both directions:

### A. The Request (HTTP -> JSON)

When the ALB receives the HTTP request, it packages all the web data into a large JSON dictionary and passes it to the Lambda function as the `event` object.
This JSON event includes:

* `httpMethod` (e.g., GET, POST)
* `path` (e.g., `/api/users`)
* `queryStringParameters` (e.g., `?id=123`)
* `headers` (e.g., User-Agent, Content-Type)
* `body` (the payload, which may be Base64 encoded)

### B. The Response (JSON -> HTTP)

Your Lambda function cannot simply `return "Hello World"`. If it does, the ALB will not know how to translate it back to a web browser, and it will throw a **502 Bad Gateway** error.
Your Python code *must* return a specifically formatted dictionary containing the `statusCode` and `body`.

---

## 2. Multi-Value Headers and Query Strings

By default, if a client sends an HTTP request with duplicate query string keys (e.g., `[https://my-alb.com/api?color=red&color=blue](https://my-alb.com/api?color=red&color=blue)`), the ALB will only pass the **last** value (`color: blue`) to your Lambda function.

To capture both values, you must enable a specific setting on your ALB Target Group called **Multi-Value Headers**.

When this is enabled, the ALB changes the structure of the JSON it sends to Lambda. Instead of standard key-value pairs, it passes arrays: `"multiValueQueryStringParameters": {"color": ["red", "blue"]}`.

---

## 3. Security: The Resource-Based Policy

When you connect an ALB to a Lambda function in the AWS Console, AWS silently handles the permissions for you. However, you must understand what is happening under the hood.

The ALB needs permission to trigger your code. To grant this, you attach a **Resource-Based Policy** directly to the Lambda function. This policy explicitly states: *"Allow the `elasticloadbalancing.amazonaws.com` service to perform `lambda:InvokeFunction`, but only if the request comes from the specific ARN of my Target Group."*

---

## 4. Boto3 Implementation & Code Handlers

Here is the Python code for a Lambda function designed to sit behind an ALB, followed by the `boto3` command required to grant the ALB permission to invoke it.

### The Python Lambda Handler

```python
import json

def lambda_handler(event, context):
    # 1. Print the event to CloudWatch to see the JSON payload from the ALB
    print(f"Received request from ALB: {json.dumps(event)}")
    
    # 2. Extract data from the ALB JSON structure
    http_method = event.get('httpMethod', 'GET')
    query_params = event.get('queryStringParameters', {})
    
    # 3. Construct the EXACT dictionary structure the ALB requires to respond
    response_body = f"<h1>Success!</h1><p>Method: {http_method}</p>"
    
    return {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {
            "Content-Type": "text/html" # Tells the browser to render HTML, not raw text
        },
        "body": response_body
    }

```

### The Boto3 Permission Command

If you are automating your infrastructure, attaching the ALB to the Target Group is not enough. You must programmatically apply the Resource-Based Policy to the Lambda function.

```python
import boto3

lambda_client = boto3.client('lambda', region_name='us-east-1')

# Grant the ALB Target Group permission to invoke the Lambda function
response = lambda_client.add_permission(
    FunctionName='MyAlbLambdaFunction',
    StatementId='AllowALBInvocation',
    Action='lambda:InvokeFunction',
    Principal='elasticloadbalancing.amazonaws.com',
    SourceArn='arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-lambda-tg/1234567890'
)
print("✅ Resource-Based Policy applied. ALB can now invoke Lambda.")

```

---

## Interview Preparation: ALB + Lambda

### Summary

Expect troubleshooting questions regarding 502 Bad Gateway errors, passing duplicate parameters, and resolving invocation permission failures.

### Q&A Details

**Q1: We routed an Application Load Balancer to a new AWS Lambda target group. The Lambda function executes perfectly and prints "Success" in CloudWatch Logs, but the end-user receives a `502 Bad Gateway` error in their browser. What is the most likely cause?**
**Answer:** The Lambda function is returning improperly formatted data. When integrating with an ALB, the Lambda function cannot return raw strings or generic objects. It must return a specifically formatted JSON dictionary containing a valid `statusCode` (e.g., 200) and a `body` field. If this format is missing, the ALB cannot translate the response back to HTTP and defaults to a 502 error.

**Q2: A web application passes multiple filters in the URL, such as `?status=active&status=pending`. The Python backend running on Lambda is only receiving the `pending` value. How do you resolve this at the infrastructure layer?**
**Answer:** You must enable the **Multi-Value Headers** attribute on the ALB's Target Group. This instructs the load balancer to package duplicate query string keys (and HTTP headers) into an array (e.g., `["active", "pending"]`) inside the JSON event payload sent to Lambda, rather than overwriting the previous values.

**Q3: You use AWS CLI to create an ALB, a Target Group, and a Lambda function. You successfully register the Lambda function to the Target Group. However, the ALB health checks are failing and traffic is not reaching the function. What security step was missed?**
**Answer:** The ALB lacks the necessary permissions to trigger the function. You must attach a **Resource-Based Policy** to the Lambda function (using the `AddPermission` API) that explicitly allows the `elasticloadbalancing.amazonaws.com` service principal to perform the `lambda:InvokeFunction` action.

---
