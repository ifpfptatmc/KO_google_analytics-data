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
        dimension_filter={
            "filter": {
                "field_name": "eventName",
                "string_filter": {
                    "match_type": "EXACT",
                    "value": event_name
                }
            }
        },
        date_ranges=[{"start_date": "2024-01-01", "end_date": "2024-12-31"}]
    )
    response = client.run_report(request)
    return response

def save_to_csv(response, event_responses):
    rows = []
    for row in response.rows:
        date = row.dimension_values[0].value
        active_users = row.metric_values[0].value
        avg_session_duration = row.metric_values[1].value
        bounce_rate = row.metric_values[2].value
        event_counts = [event_resp.rows[i].metric_values[0].value for i, event_resp in enumerate(event_responses)]
        rows.append([date, active_users, avg_session_duration, bounce_rate] + event_counts)
    
    columns = ["date", "activeUsers", "averageSessionDuration", "bounceRate"] + [f"{event_name}_count" for event_name in CUSTOM_EVENTS]
    df = pd.DataFrame(rows, columns=columns)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    # Add last updated time
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.loc[len(df)] = ["Last updated", "", last_updated, "", ""] + ["" for _ in CUSTOM_EVENTS]
    
    df.to_csv('analytics_data.csv', index=False)

def main():
    print(f"Using PROPERTY_ID: {PROPERTY_ID}")
    client = initialize_analyticsdata()
    print(f"Using KEY_FILE_CONTENT: {KEY_FILE_CONTENT[:10]}... (truncated for security)")
    response = get_report(client)
    event_responses = [get_event_report(client, event_name) for event_name in CUSTOM_EVENTS]
    save_to_csv(response, event_responses)
    print("Data fetched and saved to analytics_data.csv successfully.")

if __name__ == "__main__":
    main()
