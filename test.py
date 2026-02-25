import pandas as pd
import folium
import math

# --- 1. ตั้งค่าพื้นฐาน ---
depot = (13.998, 100.529) 
max_weight = 50.0
colors = ['red', 'blue', 'green', 'orange', 'purple', 'cadetblue']

# อ่านข้อมูล
try:
    df = pd.read_csv('data.csv')
except FileNotFoundError:
    print("Error: ไม่พบไฟล์ data.csv")
    exit()

def get_dist(p1, p2):
    d = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    return d * 111 

def create_map(truck_routes, filename):
    m = folium.Map(location=depot, zoom_start=12)
    folium.Marker(depot, popup='FLASH HUB', icon=folium.Icon(color='black', icon='home')).add_to(m)
    total_dist = 0
    for i, route in enumerate(truck_routes):
        color = colors[i % len(colors)]
        path = [depot]
        curr_pos = depot
        for c in route:
            c_pos = (c['lat'], c['long'])
            total_dist += get_dist(curr_pos, c_pos)
            path.append(c_pos)
            folium.Marker(c_pos, popup=f"{c['name']} ({c['weight']}kg)", 
                          icon=folium.Icon(color=color)).add_to(m)
            curr_pos = c_pos
        total_dist += get_dist(curr_pos, depot)
        path.append(depot)
        folium.PolyLine(path, color=color, weight=5, opacity=0.8).add_to(m)
    m.save(filename)
    return total_dist

# --- 2. แบบที่ 1: First-Come, First-Served (FCFS) ---
customers_fcfs = df.to_dict('records')
routes_fcfs = []
temp_customers = customers_fcfs.copy()

while temp_customers:
    route = []
    current_w = 0
    while temp_customers and (current_w + temp_customers[0]['weight'] <= max_weight):
        c = temp_customers.pop(0)
        route.append(c)
        current_w += c['weight']
    routes_fcfs.append(route)

dist_fcfs = create_map(routes_fcfs, 'map_fcfs.html')

# --- 3. แบบที่ 2: Smart Algorithm (Greedy) ---
customers_algo = df.to_dict('records')
routes_algo = []
remaining = customers_algo.copy()

while remaining:
    route = []
    current_w = 0
    current_pos = depot
    while True:
        next_c = None
        best_d = float('inf')
        for c in remaining:
            d = get_dist(current_pos, (c['lat'], c['long']))
            if d < best_d and (current_w + c['weight'] <= max_weight):
                best_d = d
                next_c = c
        if next_c:
            route.append(next_c)
            current_w += next_c['weight']
            current_pos = (next_c['lat'], next_c['long'])
            remaining.remove(next_c)
        else:
            break
    routes_algo.append(route)

total_dist_algo = create_map(routes_algo, 'map_algorithm.html')

# --- 4. แสดงผลลัพธ์ใน Terminal ---

# โชว์ฝั่ง FCFS ก่อน
print("\n" + "="*60)
print("📦 รายงานการเดินรถแบบ FCFS (จัดตามลำดับสั่งซื้อ)")
print("="*60)
for i, route in enumerate(routes_fcfs):
    names = " -> ".join([c['name'] for c in route])
    w = sum([c['weight'] for c in route])
    print(f"คันที่ {i+1}: {names} | รวม {w} kg")

# โชว์ฝั่ง Smart ตาม
print("\n" + "="*60)
print("🚀 รายงานการเดินรถแบบ Smart Algorithm (จัดตามความใกล้)")
print("="*60)
for i, route in enumerate(routes_algo):
    names = " -> ".join([c['name'] for c in route])
    w = sum([c['weight'] for c in route])
    color_name = colors[i % len(colors)]
    print(f"คันที่ {i+1} [สี{color_name}]: {names} | รวม {w} kg")

# ตารางสรุป
print("\n" + "📊 สรุปการเปรียบเทียบ".center(60, "="))
print(f"{'หัวข้อ':<25} | {'แบบ FCFS':<15} | {'แบบ Smart':<15}")
print("-" * 60)
print(f"{'ระยะทางรวม (กม.)':<25} | {dist_fcfs:>13.2f} | {total_dist_algo:>13.2f}")
print(f"{'จำนวนรถที่ใช้':<25} | {len(routes_fcfs):>13} | {len(routes_algo):>13}")
print("-" * 60)

improvement = ((dist_fcfs - total_dist_algo) / dist_fcfs) * 100
print(f"✅ ผลลัพธ์: อัลกอริทึม Smart ช่วยประหยัดระยะทางได้: {improvement:.2f}%")
print("="*60)