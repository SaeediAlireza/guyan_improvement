from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from model import model, schemas
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy import update

from util import util


router = APIRouter(tags=["phone-number-owner"], prefix="/phone-number-owners")


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_phone_number_owner(
    request: schemas.PhoneNumberOwnerAddRequest,
    db: Session = Depends(util.get_db),
):
    new_phone_number_owner = model.PhoneNumberOwner(
        fname=request.fname, lname=request.lname, email=request.email
    )
    PhoneNumberOwner_exist = (
        db.query(model.PhoneNumberOwner)
        .filter(
            model.PhoneNumberOwner.PhoneNumberOwner_name
            == new_phone_number_owner.PhoneNumberOwner_name
        )
        .first()
    )

    if PhoneNumberOwner_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="PhoneNumberOwner exists"
        )
    else:
        db.add(new_phone_number_owner)
        db.commit()
        db.refresh(new_phone_number_owner)
        return new_phone_number_owner


@router.get("/all", response_model=List[schemas.PhoneNumberOwnerInfoResponse])
def get_all_phone_number_owners(
    response: Response,
    db: Session = Depends(util.get_db),
):
    PhoneNumberOwners = db.query(model.PhoneNumberOwner).all()
    if not PhoneNumberOwners:
        response.status_code = status.HTTP_404_NOT_FOUND
    return PhoneNumberOwners


@router.get(
    "/{PhoneNumberOwner_id}", response_model=schemas.PhoneNumberOwnerInfoResponse
)
def get_phone_number_owner_by_id(
    PhoneNumberOwner_id: int,
    response: Response,
    db: Session = Depends(util.get_db),
):

    PhoneNumberOwner = (
        db.query(model.PhoneNumberOwner)
        .filter(model.PhoneNumberOwner.id == PhoneNumberOwner_id)
        .first()
    )

    if not PhoneNumberOwner:
        response.status_code = status.HTTP_404_NOT_FOUND
    return PhoneNumberOwner


@router.put("update")
def update_phone_number_owner(
    response: Response,
    request: schemas.PhoneNumberOwnerUpdateRequest,
    db: Session = Depends(util.get_db),
):
    PhoneNumberOwner = (
        db.query(model.PhoneNumberOwner)
        .filter(model.PhoneNumberOwner.id == request.id)
        .first()
    )
    if not PhoneNumberOwner:
        response.status_code = status.HTTP_404_NOT_FOUND
    PhoneNumberOwner.name = request.name
    PhoneNumberOwner.email = request.email

    db.commit()
    db.refresh(PhoneNumberOwner)
    return PhoneNumberOwner


@router.delete("/delete/{PhoneNumberOwner_id}")
def delete_phone_number_owner_by_id(
    PhoneNumberOwner_id: int,
    response: Response,
    db: Session = Depends(util.get_db),
):
    PhoneNumberOwner = (
        db.query(model.PhoneNumberOwner)
        .filter(model.PhoneNumberOwner.id == PhoneNumberOwner_id)
        .first()
    )
    if not PhoneNumberOwner:
        response.status_code = status.HTTP_404_NOT_FOUND
    db.delete(PhoneNumberOwner)
    db.commit()
    return {"detail": "Item deleted successfully"}
