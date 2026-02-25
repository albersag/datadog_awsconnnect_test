import os
import json
import urllib.request
import time

def lambda_handler(event, context):

    api_key = os.environ.get('DD_API_KEY')
    dd_site = os.environ.get('DD_SITE', 'datadoghq.eu')
    #details = event.get('Details', {})
    #contact_data = details.get('ContactData', {})
    #attributes = contact_data.get('Attributes', {})
    attributes = event.get('Details', {}).get('ContactData', {}).get('Attributes', {})

#    company_name = event.get('company_name', 'Unknown')
    company_name = attributes.get('CompanyName', 'Datadog')

    if not api_key:
        print("FAILED: DD_API_KEY is missing.")
        return {"error": "Missing API Key"}

    print(f"Targeting Datadog Site: {dd_site} for Company: {company_name}")
    
    # API Endpoint for Metrics
    url = f"https://api.{dd_site}/api/v1/series"
    
    headers = {
        "Content-Type": "application/json",
        "DD-API-KEY": api_key
    }
    
    # Simple payload
    payload = {
        "series": [
            {
                "metric": "callcenter.calls.incoming",
                "points": [[int(time.time()), 1]],
                "type": "count",
                "tags":[
                        f"company_name:{company_name}",
                        "region:eu-central-1",
                        "environment:production",
                        "service:phone-system",                     
                        "source:callcenter"
    ]
            }
        ]
    }
    
    # 3. Send Request
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            print(f"Datadog API Response: {response.status} {response.read().decode('utf-8')}")
            return "SUCCESS: Metric sent manually."
    except Exception as e:
        print(f"FAILED to reach Datadog: {e}")
        return f"FAILED: Could not reach Datadog. {e}"

