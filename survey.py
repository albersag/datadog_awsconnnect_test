import os
import time
from datadog_lambda.wrapper import datadog_lambda_wrapper 
from datadog_lambda.metric import lambda_metric
import json  

@datadog_lambda_wrapper
def lambda_handler(event, context):
    # 1. Extract Attributes from the Connect Event
    # Note: These are case-sensitive. Ensure 'SurveyScore' matches your Connect block.
    attributes = event.get('Details', {}).get('ContactData', {}).get('Attributes', {})
    
    # We use a default of '0' if no score is found to avoid crashes
    score = attributes.get('SurveyScore', '0')
    customer_id = attributes.get('CustomerID','unknown')
    contact_id = event.get('Details', {}).get('ContactData', {}).get('ContactId', 'unknown')
    
    try:
        # 2. Convert to integer for Datadog
        score_val = int(score)
        
        # 3. Ship Metric A: The Score (for CSAT averages)
        lambda_metric(
            "callcenter.survey.score", 
            score_val, 
            tags=[
                'env:prod', 
#                f'contact_id:{contact_id}',
                'survey_type:post_call',
                f'score:{score_val}'
#                f'customer_id:{customer_id}'
            ]
        )    
        
        # 4. Ship Metric B: The Response Count
        lambda_metric(
            "callcenter.survey.responses", 
            1, 
            tags=[
                'env:prod', 
                'survey_type:post_call'
            ]
        )
        
        print(json.dumps({
            "message": "Survey Result Processed",
            "contact_id": contact_id,
            "customer_id": customer_id,
            "score": score_val,
            "env": "prod",
            "survey_type": "post_call"
        }))

    except ValueError:
        # This catches cases where 'score' isn't a number
        print(f"Invalid score received: {score}. Skipping metric submission.")
        
    return {
        "status": "SurveyRecorded",
        "received_score": score,
        "ContactID": contact_id
        }
