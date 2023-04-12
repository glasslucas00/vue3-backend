#!/usr/bin/python3

from typing import List

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from api import abnorm
from database import configuration
from schema import schemas
# from schema.oa2 import get_current_user


router = APIRouter(tags=["Abnorm"], prefix="/abnorm")
get_db = configuration.get_db
# get_db = configuration.get_db


@router.get("/", response_model=List[schemas.Abnorm])
def get_all_blogs(db: Session = Depends(get_db)):
    """
    Get all blogs

    Args:
        db (Session, optional): Database session. Defaults to None.
        current_user (schemas.User, optional): Current user. Defaults to None.

    Returns:
        List[schemas.ShowBlog]: List of blogs
    """
    return abnorm.get_all(db)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(
    request: schemas.Abnorm,
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
    return abnorm.create(request, db)

@router.post("/search", status_code=status.HTTP_200_OK)
def search(
    request: schemas.AbnormSearchTable,
    db: Session = Depends(get_db),
):
    return abnorm.search(request, db)
@router.post("/searchSort", status_code=status.HTTP_200_OK)
def search(
    request: schemas.AbnormSearchDate,
    db: Session = Depends(get_db),
):
    return abnorm.searchSort(request, db)
    
@router.post("/searchStatistics", status_code=status.HTTP_200_OK)
def search(
    request: schemas.AbnormSearchTable,
    db: Session = Depends(get_db),
):
    return abnorm.Statistics(request, db)
@router.post("/searchByDate", status_code=status.HTTP_200_OK)
def search(
    request: schemas.AbnormSearchDate,
    db: Session = Depends(get_db),
):
    return abnorm.searchByDate(request, db)
@router.post("/searchByAnchor", status_code=status.HTTP_200_OK)
def search(
    request: schemas.AbnormSearchTable,
    db: Session = Depends(get_db),
):
    return abnorm.searchByAnchor(request, db)   
@router.post("/searchXG", status_code=status.HTTP_200_OK)
def search(
    request: schemas.AbnormSearchTable,
    db: Session = Depends(get_db),
):
    return abnorm.searchXG(request, db)   
@router.post("/delXG", status_code=status.HTTP_200_OK)
def delete_blog(
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


# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_blog(
#     id: int,
#     db: Session = Depends(get_db),
# ):
#     """
#     Delete a blog by id

#     Args:
#         id (int): Blog id
#         db (Session, optional): Database session. Defaults to None.
#         current_user (schemas.User, optional): Current user. Defaults to None.

#     Returns:
#         None: None
#     """
#     return blog.destroy(id, db)


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


