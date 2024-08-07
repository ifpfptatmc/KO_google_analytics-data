import os
import json
import datetime
import pandas as pd
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

# Property ID
PROPERTY_ID = "446474801"

# Path to your service account key file
KEY_FILE_CONTENT = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Initialize the Analytics Data API Client
def initialize_analyticsdata():
    credentials_info = json.loads(KEY_FILE_CONTENT)
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    client = BetaAnalyticsDataClient(credentials=credentials)
    return client

# Get a report from the Analytics Data API
def get_report(client):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[{"name": "date"}],
        metrics=[
            {"name": "activeUsers"},
            {"name": "averageSessionDuration"}  # Добавляем показатель "средняя продолжительность сеанса"
        ],
        date_ranges=[{"start_date": "2024-01-01", "end_date": "2024-12-31"}]
    )
    response = client.run_report(request)
    return response

# Save the report data to a CSV file
def save_to_csv(response):
    data = []
    for row in response.rows:
        date = datetime.datetime.strptime(row.dimension_values[0].value, '%Y%m%d').strftime('%Y-%m-%d')
        active_users = row.metric_values[0].value
        avg_session_duration = row.metric_values[1].value  # Получаем значение "средняя продолжительность сеанса"
        data.append([date, active_users, avg_session_duration])
    
    # Sort data by date
    data.sort()

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(data, columns=['date', 'activeUsers', 'averageSessionDuration'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    
    with open('analytics_data.csv', 'w') as file:
        df.to_csv(file, index=False)
        
        # Add the last updated line
        last_updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f'Last updated,{last_updated}\n')

# Main function
def main():
    print(f"Using PROPERTY_ID: {PROPERTY_ID}")
    client = initialize_analyticsdata()
    response = get_report(client)
    save_to_csv(response)
    print("Data fetched and saved to analytics_data.csv successfully.")

if __name__ == "__main__":
    main()
