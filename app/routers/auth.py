from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, oauth2, models, utls, schemas

router = APIRouter(prefix="/login", tags=["authenticator"])


@router.post("/", response_model=schemas.TokenModel)
def login(
    user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)
):
    fetched_user = (
        db.query(models.User).filter(models.User.email == user.username).first()
    )
    if not fetched_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Email or password is incorrect",
        )

    if not utls.verify_password(user.password, fetched_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Email or password is incorrect",
        )

    access_token = oauth2.create_access_token(data={"user_id": fetched_user.id})

    return {"access_token": access_token, "token_type": "bearer"}
