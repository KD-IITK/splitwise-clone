from pydantic import BaseModel, Field, EmailStr


class RequestOTP(BaseModel):
    email_id: EmailStr


class VerifyOTP(BaseModel):
    email_id: str
    otp: str = Field(pattern=r"^\d{6}$")