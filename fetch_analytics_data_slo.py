import os
import json
import requests
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
import pandas as pd
from datetime import datetime

# Property ID
PROPERTY_ID = "446474801"

# Path to your service account key file
KEY_FILE_CONTENT = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if not KEY_FILE_CONTENT:
    raise ValueError("The environment variable GOOGLE_APPLICATION_CREDENTIALS is not set or empty")

# Define custom events
CUSTOM_EVENTS = [
    "slo_click_call",
    "slo_click_facebook",
    "slo_click_inst",
    "slo_click_mail",
    "slo_click_wa",
    "slo_fill_any_form"
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
        metrics=[{"name": "newUsers"}, {"name": "averageSessionDuration"}, {"name": "bounceRate"}],
        date_ranges=[{"start_date": "2024-01-01", "end_date": "2024-12-31"}]
    )
    response = client.run_report(request)
    return response

def get_event_report(client, event_name):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[{"name": "date"}],
        metrics=[{"name": "eventCount"}],
        date_ranges=[{"start_date": "2024-01-01", "end_date": "2024-12-31"}],
        dimension_filter={
            "filter": {
                "field_name": "eventName",
                "string_filter": {
                    "match_type": "EXACT",
                    "value": event_name
                }
            }
        }
    )
    response = client.run_report(request)
    return response

def save_to_csv(response, event_responses):
    rows = []
    for row in response.rows:
        date = row.dimension_values[0].value
        new_users = row.metric_values[0].value
        avg_session_duration = float(row.metric_values[1].value)
        bounce_rate = float(row.metric_values[2].value)
        row_data = {
            "date": date,
            "newUsers": new_users,
            "averageSessionDuration": avg_session_duration,
            "bounceRate": bounce_rate
        }
        for event_name, event_response in event_responses.items():
            for event_row in event_response.rows:
                if event_row.dimension_values[0].value == date:
                    row_data[event_name] = event_row.metric_values[0].value
        rows.append(row_data)
    
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        # Преобразуем столбцы averageSessionDuration и bounceRate в числовой формат
    df["averageSessionDuration"] = pd.to_numeric(df["averageSessionDuration"], errors='coerce')
    df["bounceRate"] = pd.to_numeric(df["bounceRate"], errors='coerce')
    
    # Add last updated time
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.loc[len(df)] = {"date": "Last updated", "newUsers": "", "averageSessionDuration": last_updated, "bounceRate": "", "eventCount": ""}
    
    df.to_csv('analytics_data_slo.csv', index=False)

def main():
    print(f"Using PROPERTY_ID: {PROPERTY_ID}")
    client = initialize_analyticsdata()
    print(f"Using KEY_FILE_CONTENT: {KEY_FILE_CONTENT[:10]}... (truncated for security)")
    response = get_report(client)
    
    event_responses = {event_name: get_event_report(client, event_name) for event_name in CUSTOM_EVENTS}
    
    save_to_csv(response, event_responses)
    print("Data fetched and saved to analytics_data_slo.csv successfully.")

if __name__ == "__main__":
    main()
