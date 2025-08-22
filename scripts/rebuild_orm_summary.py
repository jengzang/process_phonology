from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.database import SessionLocal
from app.auth.models import ApiUsageLog, ApiUsageSummary


def rebuild_api_usage_summary(db: Session):
    print("🔁 開始統計 api_usage_logs → api_usage_summary")

    rows = (
        db.query(
            ApiUsageLog.user_id,
            ApiUsageLog.path,
            func.count(ApiUsageLog.id)
        )
        .filter(ApiUsageLog.user_id != None)  # 排除匿名訪問者（未登入）
        .group_by(ApiUsageLog.user_id, ApiUsageLog.path)
        .all()
    )

    print(f"📊 共獲得 {len(rows)} 條統計")

    for user_id, path, count in rows:
        summary = (
            db.query(ApiUsageSummary)
            .filter_by(user_id=user_id, path=path)
            .first()
        )
        if summary:
            summary.count = count
            summary.last_updated = datetime.utcnow()
        else:
            summary = ApiUsageSummary(
                user_id=user_id,
                path=path,
                count=count,
                last_updated=datetime.utcnow()
            )
            db.add(summary)

    db.commit()
    print("✅ 統計完成，已更新 api_usage_summary")

if __name__ == "__main__":
    db = SessionLocal()
    rebuild_api_usage_summary(db)
    db.close()