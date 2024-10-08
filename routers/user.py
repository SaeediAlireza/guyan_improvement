from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from model import model, schemas
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy import update

from util import util


router = APIRouter(tags=["user"], prefix="/users")


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_user(
    request: schemas.UserAddRequest,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    new_user = model.User(
        user_name=request.user_name,
        password=util.hash(request.password),
        name=request.name,
        email=request.email,
        user_type_id=request.user_type_id,
    )
    user_exist = (
        db.query(model.User).filter(model.User.user_name == new_user.user_name).first()
    )
    if user_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user exists")
    else:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


@router.get("/by-type/{type_id}", response_model=List[schemas.UserInfoResponse])
def get_users_by_type(
    type_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    users = db.query(model.User).filter(model.User.user_type_id == type_id).all()
    if not users:
        response.status_code = status.HTTP_404_NOT_FOUND
    return users


@router.get("/all", response_model=List[schemas.UserInfoResponse])
def get_all_users(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    users = db.query(model.User).all()
    if not users:
        response.status_code = status.HTTP_404_NOT_FOUND
    return users


@router.get("/all/head", response_model=List[schemas.UserInfoResponse])
def get_15_users(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    users = db.query(model.User).limit(10).all()
    if not users:
        response.status_code = status.HTTP_404_NOT_FOUND
    return users


@router.get("/{user_id}", response_model=schemas.UserInfoResponse)
def get_user_by_id(
    user_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):

    user = db.query(model.User).filter(model.User.id == user_id).first()

    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
    return user


@router.get(
    "/by-name/{user_name}",
    response_model=List[schemas.UserInfoResponse],
)
def get_users_by_name(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    user_name: str,
    db: Session = Depends(util.get_db),
):
    users = (
        db.query(model.User)
        .filter(model.User.name.like(f"%{user_name}%"))
        .limit(10)
        .all()
    )
    return users


@router.put("update")
def update_user(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    request: schemas.UserUpdateRequest,
    db: Session = Depends(util.get_db),
):
    user = db.query(model.User).filter(model.User.id == request.id).first()
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
    user.name = request.name
    user.email = request.email
    user.user_name = request.user_name
    user.user_type_id = request.user_type_id

    db.commit()
    db.refresh(user)
    return user


@router.put("password")
def update_user_password(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    request: schemas.UserUpdatePasswordRequest,
    db: Session = Depends(util.get_db),
):
    user = db.query(model.User).filter(model.User.id == request.id).first()
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
    user.password = util.hash(request.password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/delete/{user_id}")
def delete_user_by_id(
    user_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
    db.delete(user)
    db.commit()
    return {"detail": "Item deleted successfully"}
