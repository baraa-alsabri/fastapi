import datetime
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from . import schemas, database, models
from .config import settings
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    data_to_encode = data.copy()
    data_to_encode.update(
        {
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME_MINUTES)
        }
    )

    encoded_jwt = jwt.encode(
        data_to_encode,
        settings.ACCESS_TOKEN_SECRET_KEY,
        settings.ACCESS_TOKEN_ENCRYPTION_ALGORITHM,
    )

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(
            token,
            settings.ACCESS_TOKEN_SECRET_KEY,
            settings.ACCESS_TOKEN_ENCRYPTION_ALGORITHM,
        )
        id = payload.get("user_id")

        if not id:
            raise credentials_exception
        token_data = schemas.AccessTokenModel(id=id)
    except JWTError:
        raise credentials_exception
    else:
        return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify credential",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user
