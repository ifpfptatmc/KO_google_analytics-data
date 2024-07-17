import os
import json
import requests
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_CONTENT = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
VIEW_ID = 'G-LCRR9PBEPJ'

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

def print_response(response):
    with open('analytics_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Users', 'New Users', 'Avg Session Duration']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for report in response.get('reports', []):
            column_header = report.get('columnHeader', {})
            metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
            rows = report.get('data', {}).get('rows', [])
            
            for row in rows:
                date_range_values = row.get('metrics', [])
                date = row.get('dimensions', [])[0]
                
                for i, values in enumerate(date_range_values):
                    data = {
                        'Date': date,
                        'Users': values.get('values', [])[0],
                        'New Users': values.get('values', [])[1],
                        'Avg Session Duration': values.get('values', [])[2]
                    }
                    writer.writerow(data)

def main():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    print_response(response)

if __name__ == '__main__':
    main()
