

from sqlalchemy.orm import Session
from models import models


def get_all_Metros(db: Session):
    """
    Get all blogs

    Args:
        db (Session): Database session

    Returns:
        List[models.Blog]: List of blogs
    """
    items = db.query(models.train_info).all()
    count = len(items)
    return {"code": 200, "msg": "success", 'data': {'total': count, 'items': items}, "status": 200, }
