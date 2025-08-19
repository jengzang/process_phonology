import math
import re
import sqlite3
from typing import Union, List

from common.config import QUERY_DB_PATH, SUPPLE_DB_PATH


def fetch_dialect_region(input_data: Union[str, List[str]]) -> dict:
    if isinstance(input_data, list):
        query_str = input_data[0]  # 取數組的第一個元素
    else:
        query_str = input_data  # 如果是字符串，直接使用它

    # 連接資料庫並查詢
    conn = sqlite3.connect(QUERY_DB_PATH)
    cursor = conn.cursor()

    def query_database(db_path: str, table_name: str) -> tuple:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = f"SELECT 音典分區 FROM {table_name} WHERE 簡稱 = ?"
        cursor.execute(query, (query_str,))
        result = cursor.fetchone()
        conn.close()
        return result

    # 首先查詢主資料庫的表
    result = query_database(QUERY_DB_PATH, 'dialects')  # 假設主資料庫表名為 'dialects'

    # 如果在主資料庫中找不到結果，則查詢補充資料庫的表
    if not result:
        result = query_database(SUPPLE_DB_PATH, 'informations')  # 假設補充資料庫表名為 'informations'

    # 如果找到結果，返回音典分區；否則返回錯誤消息
    if result:
        return {"音典分區": result[0]}
    else:
        return {"error": "未找到對應的音典分區"}


import sqlite3
import math
import re

def get_coordinates_from_db(abbreviation_list, supplementary_abbreviation_list=None,
                            db_path=QUERY_DB_PATH, use_supplementary_db=False):
    # print("即將處理經緯度")

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_optimal_zoom(lat_diff, lon_diff):
        max_diff = max(lat_diff, lon_diff)
        unit_distance = 1000 * max_diff / 6
        zoom_to_distance = {
            20: 10, 19: 10, 18: 25, 17: 50, 16: 100,
            15: 200, 14: 500, 13: 1000, 12: 2000, 11: 5000,
            10: 10000, 9: 20000, 8: 30000, 7: 50000, 6: 100000,
            5: 200000, 4: 500000, 3: 1000000, 2: 2000000
        }
        for zoom, distance_threshold in zoom_to_distance.items():
            if unit_distance <= distance_threshold:
                return zoom
        return 10

    if supplementary_abbreviation_list:
        supplementary_abbreviation_list = [abbr for abbr in supplementary_abbreviation_list if abbr not in abbreviation_list]
    abbreviation_list = [abbreviation for abbreviation in abbreviation_list if abbreviation]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    result = []
    latitudes = []
    longitudes = []
    abbreviation_lat_lon_pairs = []
    abbreviation_region_pairs = {}  # 新增：簡稱對應音典分區

    # 查主數據庫
    for abbreviation in abbreviation_list:
        cursor.execute("SELECT 經緯度, 音典分區 FROM dialects WHERE 簡稱=?", (abbreviation,))
        row = cursor.fetchone()
        if row:
            lat_lon_str, region = row
            try:
                if lat_lon_str:
                    latitude, longitude = map(float, re.split(r'[,，\s;]+', lat_lon_str))
                else:
                    print(f"錯誤：{abbreviation} 的經緯度為空！")
                    latitude, longitude = None, None
                result.append((latitude, longitude))
                latitudes.append(latitude)
                longitudes.append(longitude)
                abbreviation_lat_lon_pairs.append((abbreviation, (latitude, longitude)))
                abbreviation_region_pairs[abbreviation] = region  # 加入音典分區
            except ValueError:
                print(f"無法解析經緯度：{lat_lon_str}")
        else:
            print(f"未找到簡稱：{abbreviation}")

    # 查補充數據庫（如需）
    if use_supplementary_db and supplementary_abbreviation_list:
        conn_supplementary = sqlite3.connect(SUPPLE_DB_PATH)
        cursor_supplementary = conn_supplementary.cursor()

        for abbreviation in supplementary_abbreviation_list:
            cursor_supplementary.execute("SELECT 經緯度, 音典分區 FROM informations WHERE 簡稱=?", (abbreviation,))
            row = cursor_supplementary.fetchone()
            if row:
                lat_lon_str, region = row
                try:
                    latitude, longitude = map(float, re.split(r'[，,]', lat_lon_str))
                    result.append((latitude, longitude))
                    latitudes.append(latitude)
                    longitudes.append(longitude)
                    abbreviation_lat_lon_pairs.append((abbreviation, (latitude, longitude)))
                    abbreviation_region_pairs[abbreviation] = region  # 加入音典分區
                except ValueError:
                    print(f"無法解析經緯度：{lat_lon_str}")
            else:
                print(f"未找到簡稱：{abbreviation}")
        conn_supplementary.close()

    valid_latitudes = [lat for lat in latitudes if lat is not None]
    valid_longitudes = [lon for lon in longitudes if lon is not None]

    if valid_latitudes and valid_longitudes:
        center_latitude = (max(valid_latitudes) + min(valid_latitudes)) / 2
        center_longitude = (max(valid_longitudes) + min(valid_longitudes)) / 2
        center_coordinate = [round(center_latitude, 6), round(center_longitude, 6)]

        max_lon_distance = 0
        max_lat_distance = 0
        for i in range(len(valid_longitudes)):
            for j in range(i + 1, len(valid_longitudes)):
                max_lon_distance = max(max_lon_distance,
                                       haversine(valid_latitudes[i], valid_longitudes[i], valid_latitudes[j],
                                                 valid_longitudes[i]))
        for i in range(len(valid_latitudes)):
            for j in range(i + 1, len(valid_latitudes)):
                max_lat_distance = max(max_lat_distance,
                                       haversine(valid_latitudes[i], valid_longitudes[i], valid_latitudes[i],
                                                 valid_longitudes[j]))
        max_lat_distance = round(max_lat_distance, 2)
        max_lon_distance = round(max_lon_distance, 2)
        zoom_level = get_optimal_zoom(max_lat_distance, max_lon_distance)
    else:
        center_coordinate = None
        max_lat_distance = max_lon_distance = 0
        zoom_level = None

    conn.close()

    coordinates = {
        "coordinates_locations": abbreviation_lat_lon_pairs,
        "region_mappings": abbreviation_region_pairs,  # 新增：音典分區對應
        "center_coordinate": center_coordinate,
        "max_distances": {
            "lat_km": max_lat_distance,
            "lon_km": max_lon_distance,
        },
        "zoom_level": zoom_level
    }

    return coordinates

