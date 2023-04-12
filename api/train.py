
# from fastapi import HTTPException, status
from sqlalchemy.orm import Session
# import redis   # 导入redis 模块
# import json
from models import models
# from schema import schemas
from sqlalchemy import text
from decouple import config

def get_all_Metros(db: Session):
    """
    Get all blogs

    Args:
        db (Session): Database session

    Returns:
        List[models.Blog]: List of blogs
    """
    items= db.query(models.train_info).all()
    count=len(items)
    return {"code":200,"msg":"success",'data':{'total':count,'items': items},"status": 200,}