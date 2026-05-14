from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
import bcrypt

app = FastAPI()

PEPPER = "MI_CLAVE_SUPER_SEGURA"

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str

class UserRegister(SQLModel):
    username: str
    password: str


class UserLogin(SQLModel):
    username: str
    password: str

engine = create_engine("sqlite:///database.db")

def hash_password(password: str) -> str:
    peppered_password = password + PEPPER

    hashed = bcrypt.hashpw(
        peppered_password.encode("utf-8"),
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    
    peppered_password = password + PEPPER

    return bcrypt.checkpw(
        peppered_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def create_db_and_users():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_users()

@app.post("/register")
def register(user: UserRegister):

    with Session(engine) as session:

        existing_user = session.exec(
            select(User).where(User.username == user.username)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El usuario ya existe"
            )

        new_user = User(
            username=user.username,
            hashed_password=hash_password(user.password)
        )

        session.add(new_user)
        session.commit()

        return {"message": "Usuario registrado correctamente"}

@app.post("/login")
def login(user: UserLogin):

    with Session(engine) as session:

        db_user = session.exec(
            select(User).where(User.username == user.username)
        ).first()

        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Usuario o contraseña incorrectos"
            )

        password_correct = verify_password(
            user.password,
            db_user.hashed_password
        )

        if not password_correct:
            raise HTTPException(
                status_code=401,
                detail="Usuario o contraseña incorrectos"
            )

        return {"message": "Login exitoso"}