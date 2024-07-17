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
    try:
        report = analytics.reports().batchGet(
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
        print("Report fetched successfully.")
        return report
    except Exception as e:
        print(f"Error fetching report: {e}")
        return None

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
        print('Data written to analytics_data.csv successfully.')
    except Exception as e:
        print(f'Error writing to CSV: {e}')

def main():
    try:
        print(f"Starting data fetch for VIEW_ID: {VIEW_ID}")
        analytics = initialize_analyticsreporting()
        data = get_report(analytics)
        if data:
            print("Data fetched successfully.")
            write_to_csv(data)
        else:
            print("No data fetched.")
        print('Process completed.')
    except Exception as e:
        print(f'Error occurred: {e}')

if __name__ == '__main__':
    print(f"Using VIEW_ID: {VIEW_ID}")
    print(f"Using KEY_FILE_CONTENT: {KEY_FILE_CONTENT[:100]}... (truncated for security)")
    main()
