from datadog_lambda.wrapper import datadog_lambda_wrapper 
from datadog_lambda.metric import lambda_metric
import os
import time

def lambda_handler(event, context):
  # 1. Extract the 'Parameters' or 'Attributes' from the Connect Event
    # Amazon Connect sends saved attributes in 'Details' -> 'ContactData' -> 'Attributes'
    attributes = event.get('Details', {}).get('ContactData', {}).get('Attributes', {})
    
    # Extract your specific parameters
    # Note: These keys must match the names you used in the 'Set Contact Attributes' block
    intent_name = attributes.get('Intent', 'unknown_intent')
    customer_id = attributes.get('CustomerID', 'anonymous')
    
    # 2. Extract Sentiment (if you passed it from Lex to an attribute)
    sentiment = attributes.get('sentiment', 'NEUTRAL')
    sentiment_map = {'POSITIVE': 1, 'NEUTRAL': 0, 'NEGATIVE': -1}
    sentiment_score = sentiment_map.get(sentiment, 0)
  

    lambda_metric(
        "callcenter.calls.lex",             
        1,                                  
        timestamp=int(time.time()),          
          tags = [
        f"intent:{intent_name}",
        f"customer_id:{customer_id}",
        "env:production",
        "source:callcenter"] 
    )

    return {
        'statusCode': 200,
        'body': 'Metric sent!'
    }
