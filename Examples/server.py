import zmq
import os
import json
import traceback
from datetime import datetime
import psycopg2

# Подключение к БД
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="database",
    user="postgres",
    password="12345"
)
cursor = conn.cursor()

def save_to_postgres(packet_number, timestamp, data):
    try:
        location_data = data.get("Location")
        if not location_data:
            return

        cell_info_list = data.get("CellInfo", [])

        for raw_ci in cell_info_list:
            ci = raw_ci.get("data", raw_ci)

            network_type = ci.get("type", "UNK")[:3]

            cursor.execute("""
                INSERT INTO database
                (Lat, Lon, Alt, Timestamp, type, MCC, MNC, PCI, TAC, CI, RSRP, ASU)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                float(location_data.get("Latitude", 0)),
                float(location_data.get("Longitude", 0)),
                float(location_data.get("Altitude", 0)),
                location_data.get("Timestamp", datetime.now().timestamp()),
                network_type,
                int(ci.get("MCC", 0)),
                int(ci.get("MNC", 0)),
                int(ci.get("PCI", 0)),
                int(ci.get("TAC", 0)),
                int(ci.get("CI", 0)),
                int(ci.get("RSRP", 0)),
                int(ci.get("ASU", 0))
            ))

        conn.commit()

    except Exception as exc:
        print(f"[ERROR] Ошибка записи в базу: {exc}")
        traceback.print_exc()

def run_server():
    context = zmq.Context()
    try:
        socket = context.socket(zmq.REP)
        socket.bind("tcp://0.0.0.0:2222")
        print("Сервер запущен на tcp://0.0.0.0:2222")
    except Exception as e:
        print(f"[ERROR] Ошибка запуска сервера: {e}")
        return

    packet_count = 0
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    file_path = os.path.join(logs_dir, "received_data.json")

    print("Ожидание сообщений...")

    while True:
        try:
            message_bytes = socket.recv()
            packet_count += 1

            try:
                message_str = message_bytes.decode("utf-8").strip()
                if not message_str:
                    socket.send_string("EMPTY PACKET")
                    continue

                data = json.loads(message_str)

                android_timestamp = data.get("Location", {}).get("Timestamp", datetime.now().timestamp())

                # Сохраняем в JSON файл
                full_json = {
                    "timestamp": android_timestamp,
                    "packet_number": packet_count,
                    "data": data
                }
                with open(file_path, "a", encoding="utf-8") as f:
                    json.dump(full_json, f, ensure_ascii=False)
                    f.write("\n")

                print(f"[{packet_count}] Данные записаны в JSON")

                # Сохраняем в базу
                save_to_postgres(packet_count, android_timestamp, data)
                print(f"[{packet_count}] Данные отправлены в PostgreSQL")

                socket.send_string(f"OK packet #{packet_count}")

            except json.JSONDecodeError as e:
                print(f"[{packet_count}] Ошибка JSON: {e}")
                socket.send_string("JSON ERROR")

            except Exception as e:
                print(f"[{packet_count}] Ошибка обработки пакета:", e)
                traceback.print_exc()
                socket.send_string("SERVER ERROR")

        except KeyboardInterrupt:
            print("Сервер остановлен вручную")
            break

        except Exception as e:
            print(f"Критическая ошибка: {e}")
            traceback.print_exc()
            continue

    socket.close()
    context.term()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_server()