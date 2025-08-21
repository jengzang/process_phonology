import re
import sqlite3

from common.config import SUPPLE_DB_PATH
from common.getloc_by_name_region import query_dialect_abbreviations


def get_from_submission(locations, regions, need_features):
    # 获取all_locations
    all_locations = query_dialect_abbreviations(regions, locations, db_path=SUPPLE_DB_PATH, tables="informations")

    # 连接到数据库
    conn = sqlite3.connect(SUPPLE_DB_PATH)
    cursor = conn.cursor()

    # 创建一个空的列表来存储结果
    result = []

    for location in all_locations:
        for feature in need_features:
            # 构造查询条件，增加查询 "maxValue"
            query = f"""
            SELECT "簡稱", "特徵", "值", "經緯度", "說明", "maxValue"
            FROM informations
            WHERE "簡稱" = ? AND "特徵" = ?
            """
            cursor.execute(query, (location, feature))

            # 获取查询结果
            rows = cursor.fetchall()

            # 如果查询有结果，处理并添加到结果列表
            for row in rows:
                # 解析經緯度，将字符串 "40.7128, -74.0060" 转换为列表 [40.7128, -74.0060]
                latitude_longitude = list(map(float, re.split(r'[，,]', row[3])))

                result.append({
                    "簡稱": row[0],
                    "特徵": row[1],
                    "值": row[2],
                    "maxValue": row[5],  # 直接从数据库中获取 maxValue
                    "經緯度": latitude_longitude,
                    "說明": row[4]
                })

    # 关闭数据库连接
    conn.close()

    # 返回所有匹配到的结果
    return result
