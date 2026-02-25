from datadog_lambda.metric import lambda_metric
from datadog_lambda.wrapper import datadog_lambda_wrapper

# WRAP your handler with the datadog_lambda_wrapper decorator
@datadog_lambda_wrapper
def lambda_handler(event, context):
    
    # ... your business logic ...
    #  user_id = event.get('user_id', 'unknown')
    
    # 1. SUBMIT A CUSTOM METRIC
    # lambda_metric(metric_name, value, tags=[list_of_tags])
    
    # Example: Counter (Increment)
    lambda_metric(
        "callcenter.calls.failed",  # Metric Name
        1,                          # Value
        tags=[                      # Tags (Key:Value)
            "environment:production",
            f"user_type:{event.get('type', 'standard')}"
        ]
    )

    # Example: Gauge (Current Value, like processing time or queue size)
    processing_time = 0.45 
    lambda_metric(
        "callcenter.processing_time",
        processing_time,
        tags=["region:eu-central-1"]
    )

    return {
        'statusCode': 200,
        'body': 'Metric sent!'
    }
