import httpx
from fastapi import APIRouter
from httpx import Timeout
from starlette.responses import JSONResponse

router = APIRouter()
@router.get("/{api_name}/{ip}")
async def proxy_lookup(api_name: str, ip: str):
    # 根据 API 名称选择不同的外部 API
    if api_name == "ip-api":
        url = f"http://ip-api.com/json/{ip}"
    elif api_name == "ip-sb":
        url = f"https://api.ip.sb/geoip/{ip}"
    elif api_name == "nordvpn":
        url = f"https://web-api.nordvpn.com/v1/ips/lookup/{ip}"
    else:
        return JSONResponse(content={"error": "Unknown API"}, status_code=400)

    # 设置更长的超时时间（例如 30 秒）
    timeout = Timeout(30.0, connect=10.0)  # 30秒的总超时，10秒的连接超时

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)

    if response.status_code == 200:
        data = response.json()
        # 格式化返回数据
        if api_name == "nordvpn":
            ip_info = {
                "query": data.get("ip"),
                "country": data.get("country"),
                "region": data.get("region"),
                "city": data.get("city"),
                "isp": data.get("isp"),
                "org": data.get("isp"),  # 使用 'isp' 作为 fallback
                "as": data.get("isp_asn"),
                "lat": data.get("latitude"),
                "lon": data.get("longitude")
            }
        elif api_name == "ip-api":
            ip_info = {
                "query": data.get("query"),
                "country": data.get("country"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "as": data.get("as"),
                "lat": data.get("lat"),
                "lon": data.get("lon")
            }
        elif api_name == "ip-sb":
            ip_info = {
                "query": data.get("ip"),
                "country": data.get("country"),
                "region": data.get("region"),
                "city": data.get("city"),
                "isp": data.get("isp"),
                "org": data.get("organization"),
                "as": data.get("asn_organization"),
                "lat": data.get("latitude"),
                "lon": data.get("longitude")
            }

        return JSONResponse(content=ip_info)
    else:
        return JSONResponse(content={"error": "Failed to fetch data"}, status_code=500)