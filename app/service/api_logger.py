import json
import os
import threading
import queue
import re
from datetime import datetime
from collections import defaultdict
import ast

from common.config import KEYWORD_LOG_FILE, SUMMARY_FILE, API_USAGE_FILE, API_DETAILED_JSON, API_DETAILED_FILE

# === 队列 ===
keyword_queue = queue.Queue()
detailed_queue = queue.Queue()


# === 关键词日志 ===
def log_keyword(path: str, field: str, value):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    keyword_queue.put((timestamp, path, field, value))


def log_all_fields(path: str, param_dict: dict):
    for field, value in param_dict.items():
        if value is not None and value != [] and value != "":
            log_keyword(path, field, value)


def keyword_writer():
    with open(KEYWORD_LOG_FILE, "a", encoding="utf-8") as f:
        while True:
            item = keyword_queue.get()
            if item is None:
                break
            timestamp, path, field, value = item
            line = f"{timestamp} | {path} | {field}: {repr(value)}\n"
            f.write(line)
            f.flush()


threading.Thread(target=keyword_writer, daemon=True).start()


# === 聚合关键词日志 ===
def aggregate_keyword_log():
    total_counts = defaultdict(lambda: defaultdict(int))
    daily_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(KEYWORD_LOG_FILE):
        return

    with open(KEYWORD_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                timestamp, path, rest = line.strip().split(" | ", 2)
                field_part, value_part = rest.split(": ", 1)
                field = field_part.strip()
                value = ast.literal_eval(value_part.strip())
                date = timestamp.split(" ")[0]
                if not isinstance(value, list):
                    value = [value]
                for item in value:
                    total_counts[field][item] += 1
                    daily_counts[date][field][item] += 1
            except Exception as e:
                print(f"[aggregate_keyword_log] Error: {e} | Line: {line}")

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("=== Total Summary ===\n")
        for field, keywords in total_counts.items():
            f.write(f"{field}:")
            for k, v in sorted(keywords.items(), key=lambda x: -x[1]):
                f.write(f"\n  {k}: {v}")
            f.write("\n")

        f.write("\n=== Daily Summary ===\n")
        for date in sorted(daily_counts.keys()):
            f.write(f"{date}:\n")
            for field, keywords in daily_counts[date].items():
                f.write(f"{field}:")
                for k, v in sorted(keywords.items(), key=lambda x: -x[1]):
                    f.write(f"\n  {k}: {v}")
                f.write("\n")


threading.Thread(target=aggregate_keyword_log, daemon=True).start()


# === API调用统计 ===
def update_count(path: str):
    today = datetime.now().strftime("%Y-%m-%d")
    with threading.Lock():
        if not os.path.exists(API_USAGE_FILE):
            with open(API_USAGE_FILE, "w", encoding="utf-8") as f:
                f.write("=== Total Counts ===\n")
                f.write(f"{path}\t1\n")
                f.write("\n=== Daily Counts ===\n")
                f.write(f"{today}\n{path}\t1\n")
            return

        with open(API_USAGE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_counts = defaultdict(int)
        daily_counts = defaultdict(lambda: defaultdict(int))
        section = None
        current_day = None
        for line in lines:
            line = line.strip()
            if line == "=== Total Counts ===":
                section = "total"
                continue
            elif line == "=== Daily Counts ===":
                section = "daily"
                continue
            elif section == "daily" and re.match(r"\d{4}-\d{2}-\d{2}", line):
                current_day = line
                continue
            elif section == "total" and line:
                k, v = line.split("\t")
                total_counts[k] = int(v)
            elif section == "daily" and line:
                k, v = line.split("\t")
                daily_counts[current_day][k] = int(v)

        total_counts[path] += 1
        daily_counts[today][path] += 1

        with open(API_USAGE_FILE, "w", encoding="utf-8") as f:
            f.write("=== Total Counts ===\n")
            for k, v in sorted(total_counts.items()):
                f.write(f"{k}\t{v}\n")
            f.write("\n=== Daily Counts ===\n")
            for date in sorted(daily_counts):
                f.write(f"{date}\n")
                for k, v in sorted(daily_counts[date].items()):
                    f.write(f"{k}\t{v}\n")


# === 详细响应记录入队 ===
def log_detailed_api(path, duration, status_code, ip, user_agent, referer):
    today = datetime.now().strftime("%Y-%m-%d")
    detailed_queue.put((path, duration, status_code, ip, user_agent, referer, today))


# === 后台线程写入详细响应 ===
def detailed_writer():
    # 初始化数据结构
    def init_stats():
        return {
            "count": 0, "total_time": 0.0, "status_codes": defaultdict(int),
            "ips": set(), "agents": set(), "referers": set()
        }

    # 从 JSON 加载旧数据
    if os.path.exists(API_DETAILED_JSON):
        with open(API_DETAILED_JSON, "r", encoding="utf-8") as f:
            raw = json.load(f)
            detailed_stats = defaultdict(init_stats, {
                k: {
                    "count": v["count"],
                    "total_time": v["total_time"],
                    "status_codes": defaultdict(int, v["status_codes"]),
                    "ips": set(v["ips"]),
                    "agents": set(v["agents"]),
                    "referers": set(v["referers"]),
                } for k, v in raw["detailed_stats"].items()
            })
            daily_stats = defaultdict(lambda: defaultdict(init_stats))
            for date, paths in raw["daily_stats"].items():
                for path, v in paths.items():
                    daily_stats[date][path] = {
                        "count": v["count"],
                        "total_time": v["total_time"],
                        "status_codes": defaultdict(int, v["status_codes"]),
                        "ips": set(v["ips"]),
                        "agents": set(v["agents"]),
                        "referers": set(v["referers"]),
                    }
    else:
        detailed_stats = defaultdict(init_stats)
        daily_stats = defaultdict(lambda: defaultdict(init_stats))

    while True:
        item = detailed_queue.get()
        if item is None:
            break
        path, duration, status, ip, agent, referer, date = item

        d = detailed_stats[path]
        d["count"] += 1
        d["total_time"] += duration
        d["status_codes"][status] += 1
        d["ips"].add(ip)
        d["agents"].add(agent)
        if referer:
            d["referers"].add(referer)

        d_day = daily_stats[date][path]
        d_day["count"] += 1
        d_day["total_time"] += duration
        d_day["status_codes"][status] += 1
        d_day["ips"].add(ip)
        d_day["agents"].add(agent)
        if referer:
            d_day["referers"].add(referer)

        # 写入结构化 JSON 文件（持久化）
        with open(API_DETAILED_JSON, "w", encoding="utf-8") as f:
            json.dump({
                "detailed_stats": {
                    k: {
                        "count": v["count"],
                        "total_time": v["total_time"],
                        "status_codes": dict(v["status_codes"]),
                        "ips": list(v["ips"]),
                        "agents": list(v["agents"]),
                        "referers": list(v["referers"]),
                    } for k, v in detailed_stats.items()
                },
                "daily_stats": {
                    date: {
                        path: {
                            "count": v["count"],
                            "total_time": v["total_time"],
                            "status_codes": dict(v["status_codes"]),
                            "ips": list(v["ips"]),
                            "agents": list(v["agents"]),
                            "referers": list(v["referers"]),
                        } for path, v in paths.items()
                    } for date, paths in daily_stats.items()
                }
            }, f, ensure_ascii=False, indent=2)

        # 写入可读汇总（和原来一样）
        with open(API_DETAILED_FILE, "w", encoding="utf-8") as f:
            f.write("=== Total Summary ===\n")
            for path, d in detailed_stats.items():
                avg = d["total_time"] / d["count"] if d["count"] else 0
                f.write(f"{path}\n  Count: {d['count']}\n  Avg Response Time: {avg:.3f}s\n")
                f.write(f"  Status Codes: {', '.join(f'{k}:{v}' for k, v in d['status_codes'].items())}\n")
                f.write("  IPs:\n" + ''.join(f"    - {ip}\n" for ip in sorted(d['ips'])))
                f.write("  User-Agents:\n" + ''.join(f"    - {ua}\n" for ua in sorted(d['agents'])))
                f.write("  Referers:\n" + ''.join(f"    - {r}\n" for r in sorted(d['referers'])))
                f.write("\n")
            f.write("=== Daily Summary ===\n")
            for date in sorted(daily_stats):
                f.write(f"{date}\n")
                for path, d in daily_stats[date].items():
                    avg = d["total_time"] / d["count"] if d["count"] else 0
                    f.write(f"{path}\n  Count: {d['count']}\n  Avg Response Time: {avg:.3f}s\n")
                    f.write(f"  Status Codes: {', '.join(f'{k}:{v}' for k, v in d['status_codes'].items())}\n")
                    f.write("  IPs:\n" + ''.join(f"    - {ip}\n" for ip in sorted(d['ips'])))
                    f.write("  User-Agents:\n" + ''.join(f"    - {ua}\n" for ua in sorted(d['agents'])))
                    f.write("  Referers:\n" + ''.join(f"    - {r}\n" for r in sorted(d['referers'])))
                f.write("\n")


threading.Thread(target=detailed_writer, daemon=True).start()
