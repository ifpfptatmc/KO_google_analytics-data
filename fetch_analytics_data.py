import os
import json
import requests
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_CONTENT = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
VIEW_ID = os.getenv('VIEW_ID')

def initialize_analyticsreporting():
    credentials_info = json.loads(KEY_FILE_CONTENT)
    credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    analytics = build('analyticsreporting', 'v4', credentials=credentials)
    return analytics

def get_report(analytics):
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
            {
                'viewId': VIEW_ID,
                'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
                'metrics': [{'expression': 'ga:users'}, {'expression': 'ga:newUsers'}, {'expression': 'ga:avgSessionDuration'}],
                'dimensions': [{'name': 'ga:date'}]
            }]
        }
    ).execute()

def fetch_analytics_data():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    print("Fetched analytics data:")
    print(json.dumps(response, indent=2))
    return response

def write_to_csv(data):
    try:
        with open('analytics_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Users', 'New Users', 'Average Session Duration']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for report in data.get('reports', []):
                rows = report.get('data', {}).get('rows', [])
                for row in rows:
                    date = row.get('dimensions', [])[0]
                    metrics = row.get('metrics', [])[0].get('values', [])
                    writer.writerow({
                        'Date': date,
                        'Users': metrics[0],
                        'New Users': metrics[1],
                        'Average Session Duration': metrics[2]
                    })
        print('Data written to analytics_data.csv')
    except Exception as e:
        print(f'Error writing to CSV: {e}')

def main():
    try:
        data = fetch_analytics_data()
        write_to_csv(data)
        print('Data fetched and written to analytics_data.csv')
    except Exception as e:
        print(f'Error occurred: {e}')

if __name__ == '__main__':
    print(f"Using VIEW_ID: {VIEW_ID}")
    print(f"Using KEY_FILE_CONTENT: {KEY_FILE_CONTENT[:100]}... (truncated for security)")
    main()
