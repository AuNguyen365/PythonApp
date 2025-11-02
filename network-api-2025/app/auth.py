from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import User, get_db
from app.utils import hash_password, verify_password, create_token, response


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(email: str, password: str, fullname: str = "", db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    user = User(email=email, password=hash_password(password), fullname=fullname)
    db.add(user)
    db.commit()
    return response("success", "Đăng ký thành công")


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Sai thông tin đăng nhập")
    token = create_token(user.id)
    return response("success", "Đăng nhập thành công", {"access_token": token})


@router.post("/logout")
def logout():
    return response("success", "Đăng xuất thành công")