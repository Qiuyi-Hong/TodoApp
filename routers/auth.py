from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Generator, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status

from database import Session, SessionLocal
from models import Users
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "c25f426664371679fcd7cb50e41be33ec5a22eb2c3789be6d901b50feab81121"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str | None


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db() -> Generator[Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="templates")


### Pages ###
@router.get("/login-page", status_code=status.HTTP_200_OK)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register-page", status_code=status.HTTP_200_OK)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})



### Endpoints for authentication and user management ###
def authenticate_user(username: str, password: str, db: db_dependency):
    user: Users | None = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    encode: dict[str, Any] = {"sub": username, "id": user_id, "role": role}
    expires: datetime = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
) -> dict[str, Any] | None:
    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Any | None = payload.get("sub")
        user_id: Any | None = payload.get("id")
        user_role: Any | None = payload.get("role")
        if username is None or user_id is None or user_role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number,
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> dict[str, str] | Literal["Failed Authentication"]:
    user: Users | None = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )
    else:
        token: str = create_access_token(
            user.username, user.id, user.role, expires_delta=timedelta(minutes=20)
        )
        return {"access_token": token, "token_type": "bearer"}
