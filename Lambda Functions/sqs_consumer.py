import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialize resources
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

# Configuration
QUEUE_URL = os.environ.get('QUEUE_URL')
table = dynamodb.Table('customers')

def lambda_handler(event, context):
    # 1. Manually PULL messages from the Queue
    print(f"Polling queue: {QUEUE_URL}")
    
    try:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,  # Grab up to 10 messages at once
            WaitTimeSeconds=5,       # Long polling: wait 5s if queue is empty
            VisibilityTimeout=30     # Hide msg from others for 30s while we work
        )
    except ClientError as e:
        print(f"Error accessing SQS: {e}")
        return {"error": str(e)}

    messages = response.get('Messages', [])
    print(f"Found {len(messages)} messages.")
    
    processed_results = []

    if not messages:
        return {"message": "Queue is empty, nothing to do."}

    # 2. Loop through the messages we pulled
    for msg in messages:
        receipt_handle = msg['ReceiptHandle']
        body = msg['Body']
        
        try:
            # Parse the JSON body
            payload = json.loads(body)
            phone_number = payload.get('phone')
            
            if phone_number:
                print(f"Processing Phone: {phone_number}")
                
                # 3. Query DynamoDB
                db_response = table.get_item(Key={'phone': phone_number})
                
                if 'Item' in db_response:
                    user_name = db_response['Item'].get('Name', 'Unknown')
                    print(f"FOUND: {user_name}")
                    processed_results.append({'phone': phone_number, 'Name': user_name})
                else:
                    print(f"NOT FOUND: {phone_number}")
                    processed_results.append({'phone': phone_number, 'Name': None})
            
            # 4. CRITICAL: Delete the message
            # Since we pulled this manually, we MUST delete it, 
            # otherwise it will reappear in the queue after the VisibilityTimeout.
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=receipt_handle
            )
            print("Message deleted from queue.")

        except Exception as e:
            print(f"Error processing message: {e}")
            # We do NOT delete the message here, so it can be retried later.

    return {
        "statusCode": 200,
        "processed_count": len(processed_results),
        "name": user_name
    }