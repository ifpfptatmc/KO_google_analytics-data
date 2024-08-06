import os
import json
from google.oauth2 import service_account
from google.analytics.data import BetaAnalyticsDataClient
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
        metrics=[{"name": "activeUsers"}],
        date_ranges=[{"start_date": "2023-01-01", "end_date": "2023-12-31"}]
    )
    response = client.run_report(request)
    return response

# Save the report data to a CSV file
def save_to_csv(response):
    with open('analytics_data.csv', 'w') as file:
        file.write('date,activeUsers\n')
        for row in response.rows:
            date = row.dimension_values[0].value
            active_users = row.metric_values[0].value
            file.write(f"{date},{active_users}\n")

# Main function
def main():
    print(f"Using PROPERTY_ID: {PROPERTY_ID}")
    client = initialize_analyticsdata()
    response = get_report(client)
    save_to_csv(response)
    print("Data fetched and saved to analytics_data.csv successfully.")

if __name__ == "__main__":
    main()
