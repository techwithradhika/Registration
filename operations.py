from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Create FastAPI app instance
app = FastAPI()

# Function to check if the MySQL database is connected
def is_mysql_connected():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        if connection.is_connected():
            return True
        else:
            return False
    except Error as e:
        print("Error connecting to MySQL:", e)
        return False
    finally:
        if connection.is_connected():
            connection.close()

# Decorator to check if the MySQL database is connected
def mysql_connected(func):
    def wrapper(*args, **kwargs):
        if is_mysql_connected():
            return func(*args, **kwargs)
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MySQL database is not connected")
    return wrapper

# Database connection
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost/Registration"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Register ORM model
class Register(Base):
    __tablename__ = 'Register'

    ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False)
    DateOfBirth = Column(String(10))

# Pydantic model for input data validation
class RegisterCreate(BaseModel):
    Name: str
    Email: str
    DateOfBirth: str

# Pydantic model for request body
class RegisterRequestBody(BaseModel):
    name: str
    email: str
    date_of_birth: str

# Pydantic model for response
class RegisterResponse(BaseModel):
    ID: int
    Name: str
    Email: str
    DateOfBirth: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new registration
@app.post("/register/", response_model=RegisterResponse)
@mysql_connected
def create_register(register: RegisterRequestBody, db: Session = Depends(get_db)):
    try:
        # Parse the string date to a Python date object
        date_of_birth = datetime.strptime(register.date_of_birth, "%d/%m/%Y").date()

        # Create a new Register object with the parsed date
        db_register = Register(Name=register.name, Email=register.email, DateOfBirth=date_of_birth)
        db.add(db_register)
        db.commit()
        db.refresh(db_register)

        db_register_dict = db_register.__dict__.copy()
        db_register_dict["DateOfBirth"] = register.date_of_birth

        return RegisterResponse(**db_register_dict)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

# Retrieve a registration by ID
@app.get("/register/{register_id}/", response_model=RegisterResponse)
@mysql_connected
def read_register(register_id: int, db: Session = Depends(get_db)):
    db_register = db.query(Register).filter(Register.ID == register_id).first()
    if db_register is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Register not found")
    return RegisterResponse(**db_register.__dict__)  # Converting SQLAlchemy object to Pydantic model

# Update a registration by ID
@app.put("/register/{register_id}/", response_model=RegisterResponse)
@mysql_connected
def update_register(register_id: int, register: RegisterRequestBody, db: Session = Depends(get_db)):
    db_register = db.query(Register).filter(Register.ID == register_id).first()
    if db_register is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Register not found")
    db_register.Name = register.name
    db_register.Email = register.email
    db_register.DateOfBirth = datetime.strptime(register.date_of_birth, "%d/%m/%Y").date()
    db.commit()
    db.refresh(db_register)
    return RegisterResponse(**db_register.__dict__)  # Converting SQLAlchemy object to Pydantic model

# Delete a registration by ID
@app.delete("/register/{register_id}/", response_model=RegisterResponse)
@mysql_connected
def delete_register(register_id: int, db: Session = Depends(get_db)):
    db_register = db.query(Register).filter(Register.ID == register_id).first()
    if db_register is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Register not found")
    db.delete(db_register)
    db.commit()
    return RegisterResponse(**db_register.__dict__)  # Converting SQLAlchemy object to Pydantic model
