import zmq
import os
import traceback
import json
from datetime import datetime

def run_server():
    context = zmq.Context()

    try:
        socket = context.socket(zmq.REP)
        socket.bind("tcp://0.0.0.0:2222")
        print("Сервер запущен на tcp://0.0.0.0:2222")
        print("Ожидание подключения от клиента...")
    except Exception as e:
        print("Ошибка при запуске сервера:", str(e))
        return

    packet_count = 0
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)   # создаём папку для логов

    def current_log_filename():
        today = datetime.now().strftime("%d-%m-%Y")
        return os.path.join(logs_dir, f"received_{today}.json")

    def save_to_json_file(data):
        filename = current_log_filename()
        try:
            # Создаем объект для записи
            data_with_timestamp = {
                "timestamp": datetime.now().isoformat(),
                "packet_number": packet_count,
                "data": data
            }
            
            # Записываем в файл, каждая строка - отдельный JSON объект
            with open(filename, "a", encoding="utf-8") as f:
                json.dump(data_with_timestamp, f, ensure_ascii=False)
                f.write("\n")  # Добавляем перевод строки
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения в JSON файл: {e}")
            return False

    while True:
        try:
            print("\nОжидание сообщения от клиента...")
            
            # Получаем сообщение (байты)
            message_bytes = socket.recv()
            packet_count += 1
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            # Пробуем декодировать и распарсить JSON
            try:
                message_str = message_bytes.decode('utf-8')
                data = json.loads(message_str)
                
                #print(f"\n[{timestamp}] Пакет #{packet_count}:")
                #print("Полученные данные:")
                #print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Сохраняем в файл
                if save_to_json_file(data):
                    print(f"Данные сохранены в файл")
                else:
                    print("Ошибка сохранения данных")
                    
            except json.JSONDecodeError as e:
                print(f"\n[{timestamp}] Пакет #{packet_count}: Ошибка декодирования JSON")
                print(f"Полученное сообщение: {message_str}")
                print(f"Ошибка: {e}")
                
                # Сохраняем сырые данные в текстовый файл
                filename_raw = current_log_filename().replace('.json', '_raw.txt')
                with open(filename_raw, "a", encoding="utf-8") as f:
                    f.write(f"{timestamp} - Пакет #{packet_count}:\n")
                    f.write(message_str)
                    f.write("\n\n")
                
            except UnicodeDecodeError as e:
                print(f"\n[{timestamp}] Пакет #{packet_count}: Ошибка декодирования UTF-8")
                print(f"Полученные байты: {message_bytes}")
                print(f"Ошибка: {e}")

            # Отправляем ответ клиенту
            reply = f"Данные получены успешно! Пакет #{packet_count}"
            socket.send_string(reply)
            print(f"Отправлен ответ клиенту: {reply}")

        except KeyboardInterrupt:
            print("\nСервер остановлен вручную")
            break
        except Exception as e:
            print("Ошибка во время обработки сообщения:")
            traceback.print_exc()
            continue

    socket.close()
    context.term()
    print("Сервер завершил работу")

if __name__ == "__main__":
    run_server()