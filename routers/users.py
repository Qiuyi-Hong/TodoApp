import typing

from fastapi import APIRouter, Depends, HTTPException, Path
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm.session import Session
from starlette import status

from database import SessionLocal
from models import Users

from .auth import get_current_user as get_current_authenticated_user

router = APIRouter(prefix="/users", tags=["users"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db() -> typing.Generator[Session, typing.Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = typing.Annotated[Session, Depends(get_db)]
user_dependency = typing.Annotated[
    dict[str, typing.Any] | None, Depends(get_current_authenticated_user)
]


class UserVerification(BaseModel):
    Password: str
    new_password: str = Field(min_length=6)


class UserPhoneNumberUpdate(BaseModel):
    phone_number: str = Field(max_length=20)


@router.get("/get_current_user", status_code=status.HTTP_200_OK)
async def read_current_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    else:
        return db.query(Users).filter(Users.id == user.get("id")).all()


# @router.put("/{new_password}", status_code=status.HTTP_204_NO_CONTENT)
# async def change_password(
#     user: user_dependency, db: db_dependency, new_password: str = Path(min_length=6)
# ):
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
#         )
#     else:
#         user_model: Users | None = (
#             db.query(Users).filter(Users.id == user.get("id")).first()
#         )
#         if user_model is not None:
#             user_model.hashed_password = bcrypt_context.hash(new_password)
#             db.add(user_model)
#             db.commit()
@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency, db: db_dependency, password_verification: UserVerification
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    else:
        user_model: Users | None = (
            db.query(Users).filter(Users.id == user.get("id")).first()
        )
        if user_model is not None:
            if bcrypt_context.verify(
                password_verification.Password, user_model.hashed_password
            ):
                user_model.hashed_password = bcrypt_context.hash(
                    password_verification.new_password
                )
                db.add(user_model)
                db.commit()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
                )


# @router.put("/update_phone_number", status_code=status.HTTP_204_NO_CONTENT)
# async def update_phone_number(
#     user: user_dependency, db: db_dependency, phone_number_update: UserPhoneNumberUpdate
# ):
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
#         )
#     else:
#         user_model: Users | None = (
#             db.query(Users).filter(Users.id == user.get("id")).first()
#         )
#         if user_model is not None:
#             user_model.phone_number = phone_number_update.phone_number
#             db.add(user_model)
#             db.commit()


@router.put(
    "/update_phone_number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT
)
async def update_phone_number(
    user: user_dependency, db: db_dependency, phone_number: str = Path(max_length=20)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    else:
        user_model: Users | None = (
            db.query(Users).filter(Users.id == user.get("id")).first()
        )
        if user_model is not None:
            user_model.phone_number = phone_number
            db.add(user_model)
            db.commit()