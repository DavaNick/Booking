from typing import Optional
from datetime import date, datetime
import uuid
from sqlmodel import Field, SQLModel, create_engine


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default=None)
    name: str
    surname: str
    phone_number: str
    email: str
    password: str
    reg: bool = Field(default=False)


class Restaurant(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default=None)
    name: str
    address: str


class Table(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default=None)
    restaurant_id: uuid.UUID = Field(foreign_key='restaurant.id')
    number: int
    capacity: int


class Reservation(SQLModel, table=True): 
    id: uuid.UUID = Field(primary_key=True, default=None) 
    user_id: uuid.UUID = Field(foreign_key='user.id') 
    restaurant_id: uuid.UUID = Field(foreign_key='restaurant.id') 
    user_name: str  
    table_number: int 
    reservation_date: date
    reservation_time: str 
    guests_count: int = Field(default=1) 
    special_requests: Optional[str] = Field(default=None)

class UserSelection(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default=None)
    user_id: uuid.UUID = Field(foreign_key='user.id')
    restaurant_id: uuid.UUID = Field(foreign_key='restaurant.id')


class PrintLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_number: int = Field(default=None, primary_key=False, index=True)
    name: str
    surname: str



engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)