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
# get_db = configuration.get_db



@router.get("/", response_model=List[schemas.Meas])
def get_all_meas(metro_name: str,db: Session = Depends(get_db)):
    """
    Get all blogs

    Args:
        db (Session, optional): Database session. Defaults to None.
        current_user (schemas.User, optional): Current user. Defaults to None.

    Returns:
        List[schemas.ShowBlog]: List of blogs
    """
    return metro.get_all(metro_name,db)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(
    request: schemas.Meas,
    db: Session = Depends(get_db),
):
    """
    Create a blog

    Args:
        request (schemas.Blog): Blog to create
        db (Session, optional): Database session. Defaults to None.
        current_user (schemas.User, optional): Current user. Defaults to None.

    Returns:
        schemas.Blog: Created blog
    """
    return metro.create(request, db)


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
    

# @router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Meas)
# def get_meas_by_id(
#     id_tour: int,
#     response: Response,
#     db: Session = Depends(get_db),
# ):
#     """
#     Get a blog by id

#     Args:
#         id (int): Blog id
#         response (Response): FastAPI response
#         db (Session, optional): Database session. Defaults to None.
#         current_user (schemas.User, optional): Current user. Defaults to None.

#     Returns:
#         schemas.ShowBlog: Blog
#     """
#     return metro.show(id, db)


@router.delete("/aa", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    id: int,
    db: Session = Depends(get_db),
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
    return metro.destroy(id, db)


# @router.put("/{id}", status_code=status.HTTP_202_ACCEPTED)
# def update_blog(
#     id: int,
#     request: schemas.Blog,
#     db: Session = Depends(get_db),
#     current_user: schemas.User = Depends(get_current_user),
# ):
#     """
#     Update a blog by id

#     Args:
#         id (int): Blog id
#         request (schemas.Blog): Blog to update
#         db (Session, optional): Database session. Defaults to Depends(get_db).
#         current_user (schemas.User, optional): Current user. Defaults to Depends(get_current_user).

#     Returns:
#         schemas.Blog: Updated blog
#     """
#     return blog.update(id, request, db)


