from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import SiteConfig
from schemas.item import SiteConfigSchema
import json

router = APIRouter()

@router.get("/activity_banner", response_model=SiteConfigSchema)
def get_activity_banner(db: Session = Depends(get_db)):
    config = db.query(SiteConfig).filter(SiteConfig.key == "activity_banner").first()
    if not config or not config.value:
        return SiteConfigSchema(key="activity_banner", value=None)
    return SiteConfigSchema(key="activity_banner", value=json.loads(config.value))

@router.get("/activities", response_model=SiteConfigSchema)
def get_activities(db: Session = Depends(get_db)):
    config = db.query(SiteConfig).filter(SiteConfig.key == "activities").first()
    if not config or not config.value:
        # 返回默认活动数据
        default_activities = [
            {
                "id": 1,
                "title": "新人福利",
                "subtitle": "注册即送优惠券",
                "image": "/static/images/activity_new_user.png",
                "color": "#45B7D1",
                "url": "/pages/activity/activity?id=1"
            }
        ]
        return SiteConfigSchema(key="activities", value=default_activities)
    return SiteConfigSchema(key="activities", value=json.loads(config.value)) 