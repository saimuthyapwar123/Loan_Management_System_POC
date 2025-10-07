from pydantic import BaseModel, EmailStr,StringConstraints, validator
from typing import Literal, Annotated, Union
from datetime import date, datetime

PhoneStr = Annotated[str, StringConstraints(pattern=r'^\+?\d{10,15}$')]
DOBStr = Annotated[str, StringConstraints(min_length=8, max_length=8)]

class RegisterUser(BaseModel):
    username: Union[PhoneStr, EmailStr] 
    password: DOBStr
    first_name: str
    last_name: str
    dob: date
    address: str
    email:EmailStr | None = None
    aadhar_number:int
    role: Literal["BORROWER", "ADMIN"] = "BORROWER"  # BORROWER or ADMIN

    @validator("first_name", "last_name", "address", pre=True)
    def capitalize_names(cls, v: str):
        if isinstance(v, str) and v.strip():
            return v.strip().capitalize()
        return v

    @validator("dob")
    def validate_age(cls, v: date):
        today = date.today()
        age = (today.year - v.year) - ((today.month, today.day) < (v.month, v.day))  
        # age = (year difference) - (1 if birthday not yet reached else 0)
        if age < 18:
            raise ValueError("User must be at least 18 years old to apply for a loan")
        return v
    
    @validator("aadhar_number")
    def validate_addhar(cls, v:int):
        if not 100000000000 <= v <= 999999999999:
            raise ValueError("Aadhaar must be 12 digits")
        return v


class LoginModel(BaseModel):
    username: Union[PhoneStr, EmailStr]
    password: DOBStr
    role: Literal["BORROWER", "ADMIN"] = "BORROWER"
