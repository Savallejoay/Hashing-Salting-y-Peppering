from sqlmodel import SQLModel, Field, create_engine

engine = create_engine("sqlite:///database.db")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str
    
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)