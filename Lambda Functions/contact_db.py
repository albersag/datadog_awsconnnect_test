import boto3
import json
# Initialize DynamoDB outside the handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('customers')

def lambda_handler(event, context):
    
    # 1. Get the phone number from the simple input event
    # Using .get() prevents the "KeyError" if the field is missing
    # We check for lowercase 'phone' first, then 'Phone' just in case
    target_phone = event.get('phone') 

    # 2. Query DynamoDB
    response = table.get_item(Key={'phone': target_phone})

    # 3. Return the Name and Phone if found
    if 'Item' in response:
        return response['Item']
    else:
        return f"No customer found for {target_phone}"
