import zmq
import os
import traceback
from datetime import datetime

def run_server():
    context = zmq.Context()

    try:
        socket = context.socket(zmq.REP)
        socket.bind("tcp://0.0.0.0:2222")  
        print("Сервер запущен на tcp://0.0.0.0:2222")
        print("Ожидание подключений от клиентов")
    except Exception as e:
        print("Ошибка при запуске сервера:", str(e))
        return

    packet_count = 0
    filename = "received_data.txt"

    if os.path.exists(filename):
        print(f"Файл {filename} уже существует. Он будет перезаписан.")
        open(filename, "w", encoding="utf-8").close()

    def print_saved_data():
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                if content:
                    print(content)
                else:
                    print("Файл пуст")

    while True:
        try:
            print("Ожидание сообщения от клиента")
            message = socket.recv_string()
            packet_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"[{timestamp}] Пакет #{packet_count}: {message}")

            try:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(f"{timestamp} - Пакет #{packet_count}: {message}\n")
                print(f"Сообщение сохранено в {filename}")
            except Exception as file_err:
                print("Ошибка записи в файл:", str(file_err))

            reply = f"Hello from Server! Получено пакетов #{packet_count}"
            socket.send_string(reply)
            print(f"Отправлен ответ клиенту: {reply}")

            if packet_count % 5 == 0:
                print_saved_data()           #выводим сохраненные данные

        except KeyboardInterrupt:
            print("\nСервер остановлен вручную")
            print_saved_data()
            break
        except Exception as e:
            print("Ошибка во время обработки сообщения")
            traceback.print_exc()
            continue

    socket.close()
    context.term()
    print("Сервер завершил работу")

if __name__ == "__main__":
    run_server()