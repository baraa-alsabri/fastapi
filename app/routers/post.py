from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model= list[schemas.PostOutModel])
def get_posts(
    db: Session = Depends(get_db),
    current_user: schemas.AccessTokenModel = Depends(oauth2.get_current_user),
    limit: int = 3,
    search: Optional[str] = "",
):
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label('votes'))
        .filter(models.Post.content.contains(search))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .limit(limit)
        .all()
    )

    return posts


@router.get("/{id}", response_model=schemas.PostResponseModel)
def get_post(id: int, db: Session = Depends(get_db)):
    post = (db.query(models.Post)
        .filter(models.Post.id == id)
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id: {id} not found")

    return post


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponseModel
)
def create_post(
    post: schemas.PostModel,
    db: Session = Depends(get_db),
    current_user: schemas.AccessTokenModel = Depends(oauth2.get_current_user),
):
    new_post = models.Post(user_id=current_user.id, **post)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete("/{id}")
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.AccessTokenModel = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} not found",
        )
    if current_user.id != post.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()
    return post_query.first()


@router.put("/{id}", response_model=schemas.PostResponseModel)
def update_post(
    id: int,
    post: schemas.PostModel,
    db: Session = Depends(get_db),
    current_user: schemas.AccessTokenModel = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} not found",
        )
    if current_user.id != post.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()
