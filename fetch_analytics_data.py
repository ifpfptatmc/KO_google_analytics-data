import os
import json
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Получение содержимого JSON ключа из переменной окружения
keyfile_dict = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'))

# Создание учетных данных из JSON ключа
credentials = service_account.Credentials.from_service_account_info(
    keyfile_dict,
    scopes=['https://www.googleapis.com/auth/analytics.readonly']
)

# ID представления Google Analytics
VIEW_ID = 'YOUR_VIEW_ID'

# Создание клиента API
analytics = build('analyticsreporting', 'v4', credentials=credentials)

# Запрос данных
response = analytics.reports().batchGet(
    body={
        'reportRequests': [
            {
                'viewId': VIEW_ID,
                'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
                'metrics': [
                    {'expression': 'ga:users'},
                    {'expression': 'ga:newUsers'},
                    {'expression': 'ga:avgSessionDuration'}
                ],
                'dimensions': [{'name': 'ga:date'}]
            }
        ]
    }
).execute()

# Обработка ответа и сохранение в CSV
report = response.get('reports', [])[0]
header = [h['name'] for h in report['columnHeader']['dimensions']] + \
         [h['name'] for h in report['columnHeader']['metricHeader']['metricHeaderEntries']]
rows = [[d for d in row['dimensions']] + [m for m in row['metrics'][0]['values']] for row in report['data']['rows']]

with open('analytics_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    writer.writerows(rows)

print('Данные успешно сохранены в analytics_data.csv')
