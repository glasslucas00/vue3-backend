#!/usr/bin/python3
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api import train
from database import configuration

router = APIRouter(tags=["Metro"], prefix="/metro")
get_db = configuration.get_db


@router.get("/")
def get_all_Metros(db: Session = Depends(get_db)):
    """
    Get all blogs

    Args:
        db (Session, optional): Database session. Defaults to None.
        current_user (schemas.User, optional): Current user. Defaults to None.

    Returns:
        List[schemas.ShowBlog]: List of blogs
    """

    return train.get_all_Metros(db)
