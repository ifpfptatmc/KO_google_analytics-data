import json
import os
import pandas as pd
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from datetime import datetime

# Загрузка содержимого ключа из переменной окружения
key_file_content = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

if not key_file_content:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is missing")

credentials_info = json.loads(key_file_content)

# Создание клиента для обращения к API
def initialize_analyticsdata():
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    client = BetaAnalyticsDataClient(credentials=credentials)
    return client

PROPERTY_ID = os.getenv('VIEW_ID')

def run_report(property_id, dimensions, metrics, date_ranges):
    client = initialize_analyticsdata()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=dimensions,
        metrics=metrics,
        date_ranges=date_ranges
    )
    response = client.run_report(request)
    return response

response = run_report(
    property_id=PROPERTY_ID,
    dimensions=[{"name": "date"}],
    metrics=[
        {"name": "activeUsers"},
        {"name": "averageSessionDuration"},
    ],
    date_ranges=[{"start_date": "2024-01-01", "end_date": "2024-12-31"}],
)

def save_to_csv(response):
    rows = []
    for row in response.rows:
        rows.append({
            "date": row.dimension_values[0].value,
            "activeUsers": int(row.metric_values[0].value),
            "averageSessionDuration": float(row.metric_values[1].value),
        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.sort_values("date")

    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_row = {"date": "Last updated", "activeUsers": "", "averageSessionDuration": last_updated}
    df = df.append(last_row, ignore_index=True)
    
    df.to_csv("analytics_data.csv", index=False)

save_to_csv(response)
