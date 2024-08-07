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
    metrics = [
        {"name": "activeUsers"},
        {"name": "averageSessionDuration"},
        {"name": "bounceRate"}
    ]

    custom_events = [
        "slo_click_call", 
        "slo_click_facebook", 
        "slo_click_inst", 
        "slo_click_mail", 
        "slo_click_wa", 
        "slo_fill_any_form"
    ]

    for event in custom_events:
        metrics.append({"name": "eventCount", "expression": f"eventCount/{event}"})

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[{"name": "date"}],
        metrics=metrics,
        date_ranges=[{"start_date": "2024-01-01", "end_date": "2024-12-31"}]
    )
    response = client.run_report(request)
    return response

def save_to_csv(response):
    rows = []
    for row in response.rows:
        date = row.dimension_values[0].value
        active_users = row.metric_values[0].value
        avg_session_duration = row.metric_values[1].value
        bounce_rate = row.metric_values[2].value
        custom_event_counts = [row.metric_values[i].value for i in range(3, 3 + len(custom_events))]
        rows.append([date, active_users, avg_session_duration, bounce_rate] + custom_event_counts)
    
    columns = ["date", "activeUsers", "averageSessionDuration", "bounceRate"] + custom_events
    df = pd.DataFrame(rows, columns=columns)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    # Add last updated time
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.loc[len(df)] = ["Last updated"] + [""] * (len(columns) - 1) + [last_updated]
    
    df.to_csv('analytics_data.csv', index=False)

def main():
    print(f"Using PROPERTY_ID: {PROPERTY_ID}")
    client = initialize_analyticsdata()
    print(f"Using KEY_FILE_CONTENT: {KEY_FILE_CONTENT[:10]}... (truncated for security)")
    response = get_report(client)
    save_to_csv(response)
    print("Data fetched and saved to analytics_data.csv successfully.")

if __name__ == "__main__":
    main()
