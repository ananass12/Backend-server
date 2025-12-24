
# Тестовая отправка данных в БД через файл
# Интегрировано в сервер

import json
import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="database",
    user="postgres",
    password="12345"
)
cursor = conn.cursor()

with open("received_data.json", "r", encoding="utf-8") as file:
    for line in file:
        try:
            data = json.loads(line.strip())

            timestamp = data['timestamp']
            packet_number = data['packet_number']
            location_data = data['data']['Location']
            cell_info_list = data['data']['CellInfo']

            server_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

            for raw_ci in cell_info_list:

                #поддержка двух форматов
                if "data" in raw_ci:
                    ci = raw_ci["data"]
                else:
                    ci = raw_ci

                network_type = ci.get('type', 'UNK')[:3]

                cursor.execute("""
                    INSERT INTO database
                    (Lat, Lon, Alt, Timestamp, type, MCC, MNC, PCI, TAC, CI, RSRP, ASU)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    float(location_data['Latitude']),
                    float(location_data['Longitude']),
                    float(location_data.get('Altitude', 0)),
                    location_data['Timestamp'],
                    network_type,
                    int(ci.get('MCC', 0)),
                    int(ci.get('MNC', 0)),
                    int(ci.get('PCI', 0)),
                    int(ci.get('TAC', 0)),
                    int(ci.get('CI', 0)),
                    int(ci.get('RSRP', 0)),
                    int(ci.get('ASU', 0))
                ))

        except Exception as e:
            print("Ошибка:", e)
            continue

conn.commit()
cursor.close()
conn.close()

print("Готово")
