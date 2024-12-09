from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, ValidationError
from datetime import date, time, datetime
from sqlalchemy import and_
from database import Reservation, engine
from sqlmodel import create_engine, select, Session
from typing import Optional
import uuid

class UserCreate(BaseModel):
    name: str
    surname: str
    phone_number: str
    email: EmailStr
    password: str

    def check_password(self):
        # Проверка длины пароля
        if len(self.password) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов.")

        # Проверка на наличие хотя бы одной цифры
        if not any(char.isdigit() for char in self.password):
            raise ValueError("Пароль должен содержать хотя бы одну цифру.")

        # Проверка на использование только английских букв и цифр
        if not self.password.isalnum():
            raise ValueError("Пароль должен содержать только английские буквы и цифры.")

    def check_name_and_surname(self):
        # Проверка на длину имени и фамилии 
        if len(self.name) < 3 or len(self.surname) < 3:
            raise ValueError("Имя и Фамилия должен содержать минимум 3 символа.")
        if any(char.isdigit() for char in self.name):
            raise ValueError("Имя не должно содержать цифр")
        if any(char.isdigit() for char in self.surname):
            raise ValueError("Фамилия не должа содержать цифр")

    def check_phone_number(self):
        # Проверка на соответствие формату телефонного номера (например, 10 цифр)
        if len(self.phone_number) != 10 or not self.phone_number.isdigit():
            raise ValueError("Некорректный формат телефонного номера. Введите 10 цифр без разделителей.")
        

class ReservationCreate(BaseModel): 
    user_name: str 
    user_id: uuid.UUID 
    restaurant_id: uuid.UUID 
    table_number: int 
    reservation_date: date 
    reservation_time: str 
    guests_count: int = 1 
    special_requests: Optional[str] = None 
 
 
    def validate_user_name(self): 
        if len(self.user_name) < 3 or not self.user_name.isalpha(): 
            raise ValueError("Имя пользователя должно содержать минимум 3 буквы и не содержать цифры.") 
 
    def validate_table_number(self): 
        if self.table_number < 1 or self.table_number > 7: 
            raise ValueError("Номер стола должен быть от 1 до 7.") 
 
    def validate_guests_count(self): 
        if self.guests_count < 1 or self.guests_count > 6: 
            raise ValueError("Количество гостей должно быть от 1 до 6.") 
 
    def validate_reservation_time(self): 
        try: 
            hours, minutes = map(int, self.reservation_time.split(':')) 
            if not (0 <= hours < 24 and 0 <= minutes < 60): 
                raise ValueError("Некорректный формат времени.") 
        except ValueError: 
            raise ValueError("Некорректный формат времени. Введите время в формате ЧЧ:ММ.") 
 
    def validate_special_requests(self): 
        if self.special_requests and len(self.special_requests) > 170: 
            raise ValueError("Пожелание не должно превышать 170 символов.")
        
    def validate_reservation_date(self):
        if self.reservation_date < datetime.now().date():
            raise ValueError("Дата резервации не может быть раньше сегодняшней даты.")
    
    def validate_reservation_time(self): 
        try: 
            hours, minutes = map(int, self.reservation_time.split(':')) 
            if not (0 <= hours < 24 and 0 <= minutes < 60): 
                raise ValueError("Некорректный формат времени.") 

            # Добавляем проверку на уникальность времени бронирования для определенного ресторана и даты
            with Session(engine) as session:
                existing_reservations = session.query(Reservation).filter(
                    and_(
                        Reservation.table_number == self.table_number,
                        Reservation.restaurant_id == self.restaurant_id,
                        Reservation.reservation_date == self.reservation_date,
                        Reservation.reservation_time == self.reservation_time
                    )
                ).all()
            if existing_reservations:
                raise ValueError("Время бронирования уже занято.")

        except ValueError: 
            raise ValueError("Некорректный формат времени. Введите время в формате ЧЧ:ММ.") 



class RestaurantCreate(BaseModel):
    name: str
    address: str