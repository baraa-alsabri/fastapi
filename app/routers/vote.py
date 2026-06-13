from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, oauth2, models

router = APIRouter(prefix="/vote", tags=["votes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: schemas.AccessTokenModel = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post {vote.post_id} does not exist.')
    
    vote_query = db.query(models.Vote).filter(
        models.Vote.user_id == current_user.id, models.Vote.post_id == vote.post_id
    )

    if vote.direction == 1:
        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        if vote_query.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} has already voted for post {vote.post_id}",
            )
        else:
            db.add(new_vote)
            db.commit()
            db.refresh(new_vote)
            return {"message": "Voted successfully!"}
    elif vote.direction == 0:
        if vote_query.first():
            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message": "Unvoted successfully!"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {current_user.id} has no vote on post {vote.post_id}",
            )
