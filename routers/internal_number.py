from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from model import model, schemas
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy import update

from util import util


router = APIRouter(tags=["internal-number"], prefix="/internal-numbers")


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_internal_number(
    request: schemas.InternalNumberAddRequest,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    new_internal_number = model.InternalNumber(
        internal_number=request.internal_number,
        path=request.path,
        phone_number_id=request.phone_number_id,
    )

    db.add(new_internal_number)
    db.commit()
    db.refresh(new_internal_number)
    return new_internal_number


@router.get("/all", response_model=List[schemas.InternalNumberInfoResponse])
def get_all_internal_numbers(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    InternalNumbers = db.query(model.InternalNumber).all()
    if not InternalNumbers:
        response.status_code = status.HTTP_404_NOT_FOUND
    return InternalNumbers


@router.get("/head", response_model=List[schemas.InternalNumberInfoResponse])
def get_15_internal_numbers(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    InternalNumbers = db.query(model.InternalNumber).limit(15).all()
    if not InternalNumbers:
        response.status_code = status.HTTP_404_NOT_FOUND
    return InternalNumbers


@router.get(
    "/by-owner-name{owner_name}",
    response_model=List[schemas.InternalNumberInfoResponse],
)
def get_internal_numbers_by_owner_name(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    owner_name: str,
    db: Session = Depends(util.get_db),
):
    InternalNumbers = (
        db.query(model.InternalNumber)
        .join(model.PhoneNumber)
        .join(model.PhoneNumberOwner)
        .filter(model.PhoneNumberOwner.name.like(f"%{owner_name}%"))
        .limit(10)
        .all()
    )
    return InternalNumbers


@router.get("/{InternalNumber_id}", response_model=schemas.InternalNumberInfoResponse)
def get_internal_number_by_id(
    InternalNumber_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):

    InternalNumber = (
        db.query(model.InternalNumber)
        .filter(model.InternalNumber.id == InternalNumber_id)
        .first()
    )

    if not InternalNumber:
        response.status_code = status.HTTP_404_NOT_FOUND
    return InternalNumber


@router.put("update")
def update_internal_number(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    request: schemas.InternalNumberUpdateRequest,
    db: Session = Depends(util.get_db),
):
    InternalNumber = (
        db.query(model.InternalNumber)
        .filter(model.InternalNumber.id == request.id)
        .first()
    )
    if not InternalNumber:
        response.status_code = status.HTTP_404_NOT_FOUND
    InternalNumber.internal_number = request.internal_number
    InternalNumber.path = request.path
    InternalNumber.phone_number_id = request.phone_number_id
    db.commit()
    db.refresh(InternalNumber)
    return InternalNumber


@router.delete("/delete/{InternalNumber_id}")
def delete_internal_number_by_id(
    InternalNumber_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    InternalNumber = (
        db.query(model.InternalNumber)
        .filter(model.InternalNumber.id == InternalNumber_id)
        .first()
    )
    if not InternalNumber:
        response.status_code = status.HTTP_404_NOT_FOUND
    db.delete(InternalNumber)
    db.commit()
    return {"detail": "Item deleted successfully"}
