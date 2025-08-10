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