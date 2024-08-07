import os
import json
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
import pandas as pd
from datetime import datetime

# Property ID
PROPERTY_ID = "446462077"

# Path to your service account key file
KEY_FILE_CONTENT = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

CUSTOM_EVENTS = [
    "en_click_call",
    "en_click_facebook",
    "en_click_inst",
    "en_click_mail",
    "en_click_wa",
    "en_fill_any_form"
]

def initialize_analyticsdata():
    credentials_info = json.loads(KEY_FILE_CONTENT)
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    client = BetaAnalyticsDataClient(credentials=credentials)
    return client

def get_report(client):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[{"name": "date"}],
        metrics=[
            {"name": "activeUsers"}, 
            {"name": "averageSessionDuration"}, 
            {"name": "bounceRate"}
        ],
        date_ranges=[{"start_date": "2024-01-01", "end_date": "2024-12-31"}]
    )
    response = client.run_report(request)
    return response

def get_event_report(client, event_name):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[{"name": "date"}],
        metrics=[{"name": "eventCount"}],
        date_ranges
