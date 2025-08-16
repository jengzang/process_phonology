import os
import threading
import queue
import time
import re
from datetime import datetime
from collections import defaultdict
import ast

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# === 文件路径 ===
KEYWORD_LOG_FILE = os.path.join(log_dir, "api_keywords_log.txt")
SUMMARY_FILE = os.path.join(log_dir, "api_keywords_summary.txt")
API_USAGE_FILE = os.path.join(log_dir, "api_usage_stats.txt")
API_DETAILED_FILE = os.path.join(log_dir, "api_detailed_stats.txt")

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
    today_counts = defaultdict(lambda: defaultdict(int))
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
                    if date == today:
                        today_counts[field][item] += 1
            except Exception as e:
                print(f"[aggregate_keyword_log] Error: {e} | Line: {line}")

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("=== Total Summary ===\n")
        for field, keywords in total_counts.items():
            f.write(f"{field}:")
            for k, v in sorted(keywords.items(), key=lambda x: -x[1]):
                f.write(f"\n  {k}: {v}")
            f.write("\n")

        f.write(f"\n=== Today: {today} ===\n")
        for field, keywords in today_counts.items():
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
    detailed_stats = defaultdict(lambda: {
        "count": 0, "total_time": 0.0, "status_codes": defaultdict(int),
        "ips": set(), "agents": set(), "referers": set()
    })
    daily_stats = defaultdict(lambda: defaultdict(lambda: {
        "count": 0, "total_time": 0.0, "status_codes": defaultdict(int),
        "ips": set(), "agents": set(), "referers": set()
    }))
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
