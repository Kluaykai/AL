import pandas as pd
import folium
import math

# ===============================
# STEP 1: กำหนดค่าพื้นฐาน
# ===============================

DEPOT = (13.121175156782886, 100.91917763861443)

# ===============================
# STEP 2: โหลดข้อมูลจากไฟล์
# ===============================

def load_data(filename):
    try:
        df = pd.read_csv(filename)
        return df.to_dict('records')
    except FileNotFoundError:
        print("ไม่พบไฟล์ data.csv")
        exit()

# ===============================
# STEP 3: ฟังก์ชันคำนวณระยะทาง
# ===============================

def calculate_distance(point1, point2, show_detail=False):
    """
    คำนวณ Euclidean distance และแปลงเป็นกิโลเมตร
    ถ้า show_detail=True จะแสดงขั้นตอนคำนวณ
    """
    lat_diff = point1[0] - point2[0]
    lon_diff = point1[1] - point2[1]

    euclidean = math.sqrt(lat_diff**2 + lon_diff**2)
    distance_km = euclidean * 111

    if show_detail:
        print(f"√(({lat_diff:.6f})² + ({lon_diff:.6f})²) × 111")
        print(f"= {distance_km:.4f} km")

    return distance_km

# ===============================
# STEP 4: วิธีที่ 1 - FCFS
# ===============================

def solve_fcfs(checkpoints):
    return checkpoints.copy()

# ===============================
# STEP 5: วิธีที่ 2 - Greedy
# ===============================

def solve_greedy(checkpoints):
    remaining = checkpoints.copy()
    route = []
    current_position = DEPOT

    while remaining:
        nearest_point = None
        shortest_distance = float('inf')

        for checkpoint in remaining:
            point = (checkpoint['lat'], checkpoint['long'])
            distance = calculate_distance(current_position, point)

            if distance < shortest_distance:
                shortest_distance = distance
                nearest_point = checkpoint

        route.append(nearest_point)
        current_position = (nearest_point['lat'], nearest_point['long'])
        remaining.remove(nearest_point)

    return route

# ===============================
# STEP 6: คำนวณระยะทางรวม + รายละเอียด
# ===============================

def calculate_total_distance(route, show_detail=False):
    total_distance = 0
    current_position = DEPOT

    for index, checkpoint in enumerate(route):
        next_position = (checkpoint['lat'], checkpoint['long'])

        if show_detail:
            print(f"\nStep {index+1}:")
            print(f"จาก {current_position} → {checkpoint['name']}")

        distance = calculate_distance(current_position, next_position, show_detail)
        total_distance += distance
        current_position = next_position

    # กลับ depot
    if show_detail:
        print(f"\nกลับ Depot:")
        print(f"จาก {current_position} → DEPOT")

    distance_back = calculate_distance(current_position, DEPOT, show_detail)
    total_distance += distance_back

    if show_detail:
        print(f"\nระยะทางรวมทั้งหมด = {total_distance:.4f} km")

    return total_distance

# ===============================
# STEP 7: สร้างแผนที่ (เพิ่ม Step Number)
# ===============================

def generate_map(route, filename, line_color):
    map_object = folium.Map(location=DEPOT, zoom_start=15)

    # Depot
    folium.Marker(
        DEPOT,
        popup="START / END (Depot)",
        icon=folium.Icon(color='darkpurple', icon='home', prefix='fa')
    ).add_to(map_object)

    path = [DEPOT]

    for index, checkpoint in enumerate(route):
        location = (checkpoint['lat'], checkpoint['long'])
        path.append(location)

        folium.Marker(
            location,
            popup=f"Step {index+1}: {checkpoint['name']}",
            tooltip=f"Step {index+1}: {checkpoint['name']}",
            icon=folium.DivIcon(
                html=f"""
                <div style="width:32px;height:32px;border-radius:50%;background:{line_color};color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;box-shadow:0 2px 4px rgba(0,0,0,0.5);border:2px solid #ffffff">{index+1}</div>
                """,
                icon_size=(32, 32),
                icon_anchor=(16, 16)
            )
        ).add_to(map_object)

    path.append(DEPOT)

    folium.PolyLine(
        path,
        color=line_color,
        weight=6,
        opacity=0.9,
        tooltip="Route Direction"
    ).add_to(map_object)

    map_object.save(filename)

# ===============================
# MAIN PROGRAM
# ===============================

if __name__ == "__main__":

    checkpoints = load_data("data.csv")

    fcfs_route = solve_fcfs(checkpoints)
    greedy_route = solve_greedy(checkpoints)

    print("\n===== FCFS =====")
    print("ลำดับเส้นทาง:")
    print(" -> ".join([c['name'] for c in fcfs_route]))

    print("\nรายละเอียดการคำนวณ FCFS:")
    fcfs_distance = calculate_total_distance(fcfs_route, show_detail=True)

    print("\n===== GREEDY =====")
    print("ลำดับเส้นทาง:")
    print(" -> ".join([c['name'] for c in greedy_route]))

    print("\nรายละเอียดการคำนวณ GREEDY:")
    greedy_distance = calculate_total_distance(greedy_route, show_detail=True)

    # สร้างแผนที่
    generate_map(fcfs_route, "map_fcfs.html", "red")
    generate_map(greedy_route, "map_algorithm.html", "blue")

    # เปรียบเทียบ
    improvement = ((fcfs_distance - greedy_distance) / fcfs_distance) * 100

    print("\n" + "="*60)
    print(f"ระยะทางรวม FCFS: {fcfs_distance:.2f} km")
    print(f"ระยะทางรวม GREEDY: {greedy_distance:.2f} km")
    print(f"Greedy ประหยัดได้: {improvement:.2f}%")
    print("="*60)