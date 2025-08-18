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


def get_coordinates_from_db(abbreviation_list, supplementary_abbreviation_list=None,
                            db_path=QUERY_DB_PATH, use_supplementary_db=False):
    print("即將處理經緯度")

    # Haversine 公式計算兩點間的距離，單位為公里
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # 地球半徑，單位為公里
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c  # 返回距離，單位為公里
        return distance

    def get_optimal_zoom(lat_diff, lon_diff):
        # 使用經度和緯度差來計算最大距離
        max_diff = max(lat_diff, lon_diff)

        # 除以6得到單位距離（距離/6）
        unit_distance = 1000 * max_diff / 6

        # 根據距離尋找合適的zoom層級
        zoom_to_distance = {
            20: 10, 19: 10, 18: 25, 17: 50, 16: 100,
            15: 200, 14: 500, 13: 1000, 12: 2000, 11: 5000,
            10: 10000, 9: 20000, 8: 30000, 7: 50000, 6: 100000,
            5: 200000, 4: 500000, 3: 1000000, 2: 2000000
        }

        # 從字典中找到合適的zoom層級
        for zoom, distance_threshold in zoom_to_distance.items():
            if unit_distance <= distance_threshold:
                return zoom
        # 如果沒有找到合適的值（通常不會發生）
        return 10

    if supplementary_abbreviation_list:
        # 刪除 supplementary_abbreviation_list 中已經在 abbreviation_list 中的元素
        supplementary_abbreviation_list = [abbr for abbr in supplementary_abbreviation_list if
                                           abbr not in abbreviation_list]
    abbreviation_list = [abbreviation for abbreviation in abbreviation_list if abbreviation]

    # 連接到查詢數據庫
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 用於存儲結果的列表
    result = []
    latitudes = []
    longitudes = []
    abbreviation_lat_lon_pairs = []  # 用來存儲簡稱和經緯度的配對

    # 根據簡稱查詢經緯度（主數據庫）
    for abbreviation in abbreviation_list:
        # 執行SQL查詢，選取簡稱匹配的行並獲取經緯度
        cursor.execute("SELECT 經緯度 FROM dialects WHERE 簡稱=?", (abbreviation,))
        row = cursor.fetchone()

        # 如果找到了匹配的行，處理經緯度
        if row:
            lat_lon_str = row[0]
            try:
                # 解析經緯度字符串，將其轉換為浮點數元組
                # latitude, longitude = map(float, re.split(r'[,，\s;]+', lat_lon_str))
                if lat_lon_str:
                    latitude, longitude = map(float, re.split(r'[,，\s;]+', lat_lon_str))
                    # print(latitude, longitude)
                else:
                    # 处理 lat_lon_str 为 None 或空字符串的情况
                    print("错误：lat_lon_str 为空或为 None！")
                    # 你可以根据需要返回默认值，或者抛出异常
                    latitude, longitude = None, None
                result.append((latitude, longitude))
                latitudes.append(latitude)
                longitudes.append(longitude)
                abbreviation_lat_lon_pairs.append((abbreviation, (latitude, longitude)))  # 存儲簡稱與經緯度配對
            except ValueError:
                print(f"無法解析經緯度：{lat_lon_str}")
        else:
            print(f"未找到簡稱：{abbreviation}")

    # 如果需要，從補充數據庫中讀取數據
    if use_supplementary_db and supplementary_abbreviation_list:
        # 連接到補充數據庫
        conn_supplementary = sqlite3.connect(SUPPLE_DB_PATH)
        cursor_supplementary = conn_supplementary.cursor()

        # 使用補充的簡稱列表進行查詢
        for abbreviation in supplementary_abbreviation_list:
            # 執行SQL查詢，選取簡稱匹配的行並獲取經緯度
            cursor_supplementary.execute("SELECT 經緯度 FROM informations WHERE 簡稱=?", (abbreviation,))
            row = cursor_supplementary.fetchone()

            # 如果找到了匹配的行，處理經緯度
            if row:
                lat_lon_str = row[0]
                try:
                    # 解析經緯度字符串，將其轉換為浮點數元組
                    latitude, longitude = map(float, re.split(r'[，,]', lat_lon_str))
                    result.append((latitude, longitude))
                    latitudes.append(latitude)
                    longitudes.append(longitude)
                    abbreviation_lat_lon_pairs.append((abbreviation, (latitude, longitude)))  # 存儲簡稱與經緯度配對
                except ValueError:
                    print(f"無法解析經緯度：{lat_lon_str}")
            else:
                print(f"未找到簡稱：{abbreviation}")

        conn_supplementary.close()

    valid_latitudes = [lat for lat in latitudes if lat is not None]
    valid_longitudes = [lon for lon in longitudes if lon is not None]

    if valid_latitudes and valid_longitudes:
        # 计算中心经纬度
        center_latitude = (max(valid_latitudes) + min(valid_latitudes)) / 2
        center_longitude = (max(valid_longitudes) + min(valid_longitudes)) / 2

        # 保留6位小数
        center_coordinate = [round(center_latitude, 6), round(center_longitude, 6)]

        # 计算横向最大距离（经度差）
        max_lon_distance = 0
        max_lat_distance = 0

        # 计算最大经度距离（横向）
        for i in range(len(valid_longitudes)):
            for j in range(i + 1, len(valid_longitudes)):
                max_lon_distance = max(max_lon_distance,
                                       haversine(valid_latitudes[i], valid_longitudes[i], valid_latitudes[j],
                                                 valid_longitudes[i]))

        # 计算最大纬度距离（纵向）
        for i in range(len(valid_latitudes)):
            for j in range(i + 1, len(valid_latitudes)):
                max_lat_distance = max(max_lat_distance,
                                       haversine(valid_latitudes[i], valid_longitudes[i], valid_latitudes[i],
                                                 valid_longitudes[j]))

        # 保留2位小数
        max_lat_distance = round(max_lat_distance, 2)
        max_lon_distance = round(max_lon_distance, 2)

        # 根据最大距离计算合适的 zoom 层级
        zoom_level = get_optimal_zoom(max_lat_distance, max_lon_distance)
    else:
        center_coordinate = None
        max_lat_distance = max_lon_distance = 0
        zoom_level = None

    # 關閉數據庫連接
    conn.close()

    # 返回結果，包括經緯度與簡稱配對、中心經緯度、最大縱向和橫向距離，以及對應的zoom層級
    coordinates = {
        "coordinates_locations": abbreviation_lat_lon_pairs,  # 返回簡稱與經緯度的配對
        "center_coordinate": center_coordinate,
        "max_distances": {
            "lat_km": max_lat_distance,
            "lon_km": max_lon_distance,
        },
        "zoom_level": zoom_level  # 返回選擇的zoom層級
    }

    return coordinates
