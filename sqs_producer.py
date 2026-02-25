import json
import boto3
import os

# Initialize SQS client
sqs = boto3.client('sqs')
QUEUE_URL = os.environ['QUEUE_URL']

def lambda_handler(event, context):
    try:
        # 1. Extract phone (Input validation)
        # Note: Adjust extraction logic based on your trigger (API Gateway vs Connect)
        phone = event.get('phone') or event.get('Details', {}).get('ContactData', {}).get('CustomerEndpoint', {}).get('Address')
        
        if not phone:
            return {'statusCode': 400, 'body': 'No phone number provided'}

        # 2. Send Message to SQS
        # We wrap the data in a JSON string
        message_body = {
            'phone': phone,
            'task_type': 'lookup_user'
        }

        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message_body)
        )

        print(f"Message sent! ID: {response['MessageId']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Request queued successfully', 'id': response['MessageId']})
        }

    except Exception as e:
        print(e)
        return {'statusCode': 500, 'body': str(e)}
