#!/usr/bin/python3
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from api import abnorm
from database import configuration
from schema import schemas
router = APIRouter(tags=["Abnorm"], prefix="/abnorm")
get_db = configuration.get_db


@router.post("/search", status_code=status.HTTP_200_OK)
def search(
    request: schemas.AbnormSearchTable,
    db: Session = Depends(get_db),
):
    return abnorm.search(request, db)


@router.post("/searchStatistics", status_code=status.HTTP_200_OK)
def search(
    request: schemas.AbnormSearchTable,
    db: Session = Depends(get_db),
):
    return abnorm.fireStatistics(request, db)


@router.post("/searchByAnchor", status_code=status.HTTP_200_OK)
def searchByAnchor(
    request: schemas.AbnormSearchTable,
    db: Session = Depends(get_db),
):
    return abnorm.searchByAnchor(request, db)


@router.post("/searchXG", status_code=status.HTTP_200_OK)
def searchXG(
    request: schemas.AbnormSearchTable,
    db: Session = Depends(get_db),
):
    return abnorm.searchXG(request, db)


@router.post("/delXG", status_code=status.HTTP_200_OK)
def delXG(
    request: schemas.AbnormXG
):
    """
    Delete a blog by id

    Args:
        id (int): Blog id
        db (Session, optional): Database session. Defaults to None.
        current_user (schemas.User, optional): Current user. Defaults to None.

    Returns:
        None: None
    """
    return abnorm.delXG(request)
