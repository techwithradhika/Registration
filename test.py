from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List
from fastapi.staticfiles import StaticFiles
from pathlib import Path


# Create FastAPI app instance
app = FastAPI()

templates_directory = Path("C:/Users/radhi/Downloads/New folder/templates")

# Mount the "templates" directory as a static directory to serve HTML files
app.mount("/static", StaticFiles(directory=templates_directory), name="static")

# Database connection
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/Registration"
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

# Pydantic model for response
class RegisterResponse(BaseModel):
    ID: int
    Name: str
    Email: str
    DateOfBirth: str

# Create table if not exists
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new registration
@app.post("/register/", response_model=RegisterResponse)
def create_register(register: RegisterCreate, db: Session = Depends(get_db)):
    try:
        try:
            date_of_birth = datetime.strptime(register.DateOfBirth, "%d/%m/%Y").date()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Please provide the date in the format 'DD/MM/YYYY'.")

        # Create a new Register object with the parsed date
        db_register = Register(Name=register.Name, Email=register.Email, DateOfBirth=date_of_birth)
        db.add(db_register)
        db.commit()
        db.refresh(db_register)

        db_register_dict = db_register.__dict__.copy()
        db_register_dict["DateOfBirth"] = register.DateOfBirth

        return RegisterResponse(**db_register_dict)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
@app.get("/register/", response_model=List[RegisterResponse])
def read_all_registers(db: Session = Depends(get_db)):
    registers = db.query(Register).all()
    register_list = []
    for register in registers:
        register_dict = register.__dict__.copy()
        register_dict["DateOfBirth"] = str(register_dict["DateOfBirth"])
        register_list.append(RegisterResponse(**register_dict))
    return register_list

# Retrieve a registration by ID
@app.get("/register/{register_id}/", response_model=RegisterResponse)
def read_register(register_id: int, db: Session = Depends(get_db)):
    db_register = db.query(Register).filter(Register.ID == register_id).first()
    if db_register is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Register not found")
    
    # Convert DateOfBirth to string
    db_register_dict = db_register.__dict__.copy()
    db_register_dict["DateOfBirth"] = str(db_register_dict["DateOfBirth"])
    
    return RegisterResponse(**db_register_dict) 

# Update a registration by ID
@app.put("/register/{register_id}/", response_model=RegisterResponse)
def update_register(register_id: int, register: RegisterCreate, db: Session = Depends(get_db)):
    try:
        db_register = db.query(Register).filter(Register.ID == register_id).first()
        if db_register is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Register not found")
        
        # Attempt to parse the date string
        try:
            date_of_birth = datetime.strptime(register.DateOfBirth, "%d/%m/%Y").date()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Please provide the date in the format 'DD/MM/YYYY'.")

        db_register.Name = register.Name
        db_register.Email = register.Email
        db_register.DateOfBirth = date_of_birth
        db.commit()
        db.refresh(db_register)
        
        db_register_dict = db_register.__dict__.copy()
        db_register_dict["DateOfBirth"] = register.DateOfBirth

        return RegisterResponse(**db_register_dict)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

# Delete a registration by ID
@app.delete("/register/{register_id}/", response_model=RegisterResponse)
def delete_register(register_id: int, db: Session = Depends(get_db)):
    try:
        db_register = db.query(Register).filter(Register.ID == register_id).first()
        if db_register is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Register not found")
        
        db.delete(db_register)
        db.commit()
        db_register_dict = db_register.__dict__.copy()
        db_register_dict["DateOfBirth"] = str(db_register_dict["DateOfBirth"])

        return RegisterResponse(**db_register_dict)    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
