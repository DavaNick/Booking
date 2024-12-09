from fastapi import FastAPI, HTTPException, Request, status, Depends, Form, Cookie
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlmodel import create_engine, select, Session
from database import User, engine, Reservation, Restaurant, PrintLog
from validation import UserCreate, ReservationCreate, RestaurantCreate
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime 
import bcrypt
import jwt
import uuid
import os

app = FastAPI()

SECRET_KEY = "Raul333"


app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем папку с шаблонами
templates = Jinja2Templates(directory="templates")

# Подключаем папку с статическими файлами (изображениями)
app.mount("/static", StaticFiles(directory="./static"), name="static")

# Маршруты FastAPI
@app.get("/restorants", response_class=HTMLResponse)
async def add_res(request: Request):
    return templates.TemplateResponse("restorants.html", {"request": request})

@app.get("/select", response_class=HTMLResponse)
async def adm_reg_barat(request: Request):
    return templates.TemplateResponse("select.html", {"request": request})

@app.get("/baratie-go", response_class=HTMLResponse)
async def adm_reg_barat(request: Request):
    return templates.TemplateResponse("baratie-admin-reg.html", {"request": request})

@app.get("/florintini-go", response_class=HTMLResponse)
async def adm_reg_flo(request: Request):
    return templates.TemplateResponse("florintini-admin-reg.html", {"request": request})

@app.get("/six_floor-go", response_class=HTMLResponse)
async def adm_reg_six(request: Request):
    return templates.TemplateResponse("six_floor-admin-reg.html", {"request": request})

#--------------------------------------------------------------------------------------
#для пользователя
@app.get("/baratie", response_class=HTMLResponse)
async def read_baratie(request: Request):
    with Session(engine) as session:
        users = session.exec(select(User).order_by(-User.id).limit(1)).all()
    return templates.TemplateResponse("baratie.html", {"request": request, "users": users})

@app.get("/florintini", response_class=HTMLResponse)
async def read_florintini(request: Request):
    with Session(engine) as session:
        users = session.exec(select(User).order_by(-User.id).limit(1)).all()
    return templates.TemplateResponse("florintini.html", {"request": request, "users": users})

@app.get("/six_floor", response_class=HTMLResponse)
async def read_six_floor(request: Request):
    with Session(engine) as session:
        users = session.exec(select(User).order_by(-User.id).limit(1)).all()
    return templates.TemplateResponse("six_floor.html", {"request": request, "users": users})

@app.get("/reg", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("reg.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


def get_user_status(user_id: uuid.UUID):
    with Session(engine) as session:
        user = session.get(User, user_id)
        return user

async def get_user_token(request: Request) -> str:
    token = request.cookies.get("user_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.JWTError:
        return None



@app.get("/", response_class=HTMLResponse)
async def head(request: Request, user_token: Optional[str] = Cookie(None)):
    with Session(engine) as session:
        print_log = session.query(PrintLog).order_by(PrintLog.user_number.desc()).limit(1).first()
    print("User token from cookie:", user_token)  # Добавляем отладочную информацию
    user = None
    if user_token:
        user_id = await get_user_token(request)
        user = get_user_status(uuid.UUID(user_id))

    return templates.TemplateResponse("head.html", {"request": request, "user": user, "user_token": user_token, "print_log": print_log})

@app.get("/delete_token")
async def delete_token(request: Request, response: Response):
    response.delete_cookie("user_token")
    return templates.TemplateResponse("head.html", {"user_token": None, "request": request})


@app.get("/read_cookie")
async def read_cookie(request: Request):
    user_token = request.cookies.get("user_token")
    if user_token:
        # Выполните действия с куки, например, аутентификацию пользователя
        return {"message": "User token found in cookie: " + user_token}
    else:
        return {"message": "No user token found in cookie"}
#-------------------------------------------------------------------------------------------------
#Пост запросы
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка соответствия обычного пароля и хешированного пароля.
    """
    return plain_password

# Функция для получения пользователя по email
def get_user_by_email(email: str) -> Optional[User]:
    """
    Получение пользователя из базы данных по email.
    """
    engine = create_engine("sqlite:///database.db")  # Замените на свою базу данных
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
    return user

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/login", tags=['Authentication'])
async def login(user: UserLogin):
    # Проверяем пользователя в базе данных по мейлу
    current_time = datetime.now()
    user_number = int(current_time.timestamp())  # Преобразуем текущее время в число
    user_in_db = get_user_by_email(user.email)
    if not user_in_db:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    if not verify_password(user.password, user_in_db.password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    


    with Session(engine) as session:
        print_log = PrintLog(id=uuid.uuid4(), user_number=user_number, name=user_in_db.name, surname=user_in_db.surname)
        session.add(print_log)
        session.commit()

    # Добавляем вывод имени и фамилии пользователя
    print(f"Вошел пользователь: {user_in_db.name} {user_in_db.surname}")

    token_data = {"user_id": str(user_in_db. id)}
    token = jwt.encode(token_data, SECRET_KEY)

    return {"message": "Вход выполнен успешно", "user": {"name": user_in_db.name, "surname": user_in_db.surname}, "token": token}

@app.post("/register", response_class=HTMLResponse, tags=['Account'])
async def create_account(request: Request, user: UserCreate, response: Response):
    try:
        user.check_password()
        user.check_name_and_surname()
        user.check_phone_number()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    with Session(engine) as session:
        user_id = str(uuid.uuid4())

        hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())

        db_user = User(
            id=user_id,
            name=user.name,
            surname=user.surname,
            phone_number=user.phone_number,
            email=user.email,
            password=hashed_password.decode(),
            reg=True
        )

        session.add(db_user)
        session.commit()

        token_data = {"user_id": user_id}
        token = jwt.encode(token_data, SECRET_KEY)
        print("User token:", token)  # Выводим токен в консоль
        response.set_cookie(key="user_token", value=token, httponly=True, secure=True, samesite="Strict")

    return "Пользователь успешно зарегистрирован"

@app.post("/reservation", response_class=HTMLResponse) 
async def create_reservation(request: Request, reservation: ReservationCreate): 
    try: 
        reservation.validate_user_name() 
        reservation.validate_table_number() 
        reservation.validate_guests_count() 
        reservation.validate_reservation_time() 
        reservation.validate_special_requests() 
    except ValueError as e: 
        raise HTTPException(status_code=400, detail=str(e)) 
 
    with Session(engine) as session: 
        reservation_id = str(uuid.uuid4()) 
        db_reservation = Reservation( 
            id=reservation_id, 
            user_id=reservation.user_id, 
            restaurant_id=reservation.restaurant_id, 
            user_name=reservation.user_name, 
            table_number=reservation.table_number, 
            reservation_date=reservation.reservation_date, 
            reservation_time=reservation.reservation_time, 
            guests_count=reservation.guests_count, 
            special_requestsr=reservation.special_requests 
        ) 
 
        session.add(db_reservation) 
        session.commit() 
        session.refresh(db_reservation)

@app.post("/restaurant", response_class=HTMLResponse)
async def create_restaurant(request: Request, restaurant: RestaurantCreate):
    with Session(engine) as session:
        restaurant_id = str(uuid.uuid4())
        db_restaurant = Restaurant(
            id=restaurant_id,
            name=restaurant.name,
            address=restaurant.address
        )

        session.add(db_restaurant)
        session.commit()
        session.refresh(db_restaurant)

    return "Restaurant created successfully"

#-------------------------------------------------------------------------------------------------------
#Delete запрос

@app.delete("/reservation/delete/{reservation_id}")
def delete_reservation(reservation_id: str):
    try:
        reservation_uuid = str(reservation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reservation id")

    with Session(engine) as session:
        db_reservation = session.query(Reservation).filter(Reservation.id == reservation_uuid).first()
        if db_reservation:
            session.delete(db_reservation)
            session.commit()
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Reservation not found")

#-------------------------------------------------------------------------------------------------------
#Админки(ограничить доступ! (поправка уже ограничено)))


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    with Session(engine) as session:
        users = session.exec(select(User).order_by(User.name, User.surname)).all()

    return templates.TemplateResponse("admin.html", {"request": request, "users": users})


@app.post("/baratie-admin", response_class=HTMLResponse)
async def admin_baratie(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "Raul" and password == "Baratie378":
        with Session(engine) as session:
            reservation = session.exec(select(Reservation).where(Reservation.restaurant_id == "c563872f6def44b1b6cc7ef222250781")).all()
        return templates.TemplateResponse("baratie-admin.html", {"request": request, "reservation": reservation})
    else:
        return HTTPException(status_code=401, detail="Invalid credentials")



@app.post("/florintini-admin", response_class=HTMLResponse)
async def admin_florintini(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "flo" and password == "flo378":
        with Session(engine) as session:
            reservation = session.exec(select(Reservation).where(Reservation.restaurant_id == "c563872f6def44b1b6cc7ef222250751")).all()
        return templates.TemplateResponse("florintini-admin.html", {"request": request, "reservation": reservation})
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/six_floor-admin", response_class=HTMLResponse)
async def admin_six_floor(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "six" and password == "six378":
        with Session(engine) as session:
            reservation = session.exec(select(Reservation).where(Reservation.restaurant_id == "30bb66205ebd40f8adb92b4870897444")).all()
        return templates.TemplateResponse("six_floor-admin.html", {"request": request, "reservation": reservation})
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")