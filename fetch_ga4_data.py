import os
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest

# Замените ваш JSON ключ на соответствующую строку
key_file_content = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

credentials_info = json.loads(key_file_content)
client = BetaAnalyticsDataClient.from_service_account_info(credentials_info)

property_id = 'YOUR_PROPERTY_ID'  # Замените YOUR_PROPERTY_ID на ваш Идентификатор потока данных

request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[Dimension(name="country"), Dimension(name="city")],
    metrics=[Metric(name="activeUsers")],
    date_ranges=[DateRange(start_date="2023-01-01", end_date="2023-12-31")],
)

response = client.run_report(request)

print("Report result:")
for row in response.rows:
    print(row.dimension_values, row.metric_values)

# Сохранение результатов в CSV файл
import csv

with open('ga4_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['country', 'city', 'activeUsers']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in response.rows:
        writer.writerow({
            'country': row.dimension_values[0].value,
            'city': row.dimension_values[1].value,
            'activeUsers': row.metric_values[0].value
        })
