#!/usr/bin/python3

from typing import List

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from api import metro
from database import configuration
from schema import schemas
# from schema.oa2 import get_current_user


router = APIRouter(tags=["Meas"], prefix="/meas")
get_db = configuration.get_db


@router.post("/search", status_code=status.HTTP_200_OK)
def search(
    request: schemas.MeasSearchTable,
    db: Session = Depends(get_db),
):
    return metro.search(request, db)


@router.post("/searchChart", status_code=status.HTTP_200_OK)
def searchAll(
    request: schemas.MeasSearchTable,
    db: Session = Depends(get_db),
):
    return metro.searchChart(request, db)
