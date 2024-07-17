import os
import json
import requests
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_CONTENT = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
VIEW_ID = 'YOUR_VIEW_ID'

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

def save_to_csv(response):
    with open('analytics_data.csv', mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Users', 'New Users', 'Avg Session Duration'])
        
        for report in response.get('reports', []):
            rows = report.get('data', {}).get('rows', [])
            for row in rows:
                dimensions = row.get('dimensions', [])
                date = datetime.strptime(dimensions[0], '%Y%m%d').strftime('%Y-%m-%d')
                metrics = row.get('metrics', [])[0].get('values', [])
                writer.writerow([date] + metrics)

def main():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    save_to_csv(response)

if __name__ == '__main__':
    main()
