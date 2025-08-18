# app/main.py

import threading
import time
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.routes import setup_routes
from app.static_utils import get_resource_path, ensure_user_data  # 如果你要用它挂载静态资源
from common.config import _RUN_TYPE
from starlette.staticfiles import StaticFiles

# === 周期打印 ===
print_lock = threading.Lock()
active_requests = 0
_printer_started = False


def _periodic_printer():
    msg = (
        "\n\n##################################\n"
        "歡迎使用  方言比較 - 地理語言學  小工具\n "
        " 開發者：不羈   2025年8月\n"
        "------------------------------------\n"
        "這個窗口不能關！！這是python fastapi後端！！\n"
        "###################################"
    )
    while True:
        time.sleep(200)
        with print_lock:
            if active_requests == 0:
                print(msg)
                now = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{now}] Backend alive ✅ — 開發者: 不羈")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _printer_started
    if not _printer_started:
        _printer_started = True
        t = threading.Thread(target=_periodic_printer, daemon=True)
        t.start()
    yield  # 應用運行中


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# === 活動請求統計中介層 ===
@app.middleware("http")
async def pause_print_while_request(request: Request, call_next):
    global active_requests
    with print_lock:
        active_requests += 1
    try:
        response = await call_next(request)
        return response
    finally:
        with print_lock:
            active_requests -= 1


# === 掛載子路由與靜態資源 ===
setup_routes(app)


app.mount("/app/css", StaticFiles(directory=get_resource_path("app/css")), name="css")
app.mount("/app/js", StaticFiles(directory=get_resource_path("app/js")), name="js")
# app.mount("/app/service", StaticFiles(directory=get_resource_path("app/service")), name="make")
# app.mount("/data", StaticFiles(directory=get_resource_path("data")), name="data")
if _RUN_TYPE == 'PACK':
    app.mount("/data", StaticFiles(directory=ensure_user_data()), name="data")
