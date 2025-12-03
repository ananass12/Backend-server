import psycopg2
import json
import matplotlib.pyplot as plt

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="database",
    user="postgres",
    password="12345"
)
cursor = conn.cursor()

cursor.execute("SELECT lat, lon, rsrp FROM database")
rows = cursor.fetchall()

latitudes = [float(r[0]) for r in rows]
longitudes = [float(r[1]) for r in rows]
rsrp = [float(r[2]) for r in rows]

conn.close()

plt.figure(figsize=(8, 6))
plt.scatter(longitudes, latitudes, s=10)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("GPS координаты")
plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
plt.grid(True)
plt.show()

plt.figure(figsize=(8, 6))
sc = plt.scatter(longitudes, latitudes, c=rsrp, s=10, cmap='plasma')  
plt.colorbar(sc, label='Уровень сигнала') 
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("GPS координаты с уровнем сигнала")
plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
plt.grid(True)
plt.show()


# Чтение данных с файла json

# filename = "logs/received_data.json"
# latitudes = []
# longitudes = []

# with open(filename, "r", encoding="utf-8") as f:
#     for line in f:
#         try:
#             obj = json.loads(line.strip())
#             loc = obj["data"]["Location"]

#             latitudes.append(float(loc["Latitude"]))
#             longitudes.append(float(loc["Longitude"]))

#         except Exception as e:
#             print("Ошибка чтения строки:", e)
#             continue

# plt.figure(figsize=(8, 6))
# plt.scatter(longitudes, latitudes, s=10)
# plt.xlabel("Longitude")
# plt.ylabel("Latitude")
# plt.title("GPS координаты")
# plt.grid(True)
# plt.show()