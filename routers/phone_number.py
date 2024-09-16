from typing import Annotated, List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    UploadFile,
    File,
)

from fastapi.responses import StreamingResponse
from model import model, schemas
from sqlalchemy.orm import Session
from util import util
import pandas as pd
import io
from io import StringIO

router = APIRouter(tags=["phone number"], prefix="/phone-numbers")


@router.post("/add")
def add_phone_number(
    request: schemas.PhoneNumberAddRequest,
    db: Session = Depends(util.get_db),
):
    new_phone_number = model.PhoneNumber(
        number=request.number,
        phone_number_owner_id=request.phone_number_owner_id,
    )
    db.add(new_phone_number)
    db.commit()
    db.refresh(new_phone_number)
    return new_phone_number


@router.get("/all", response_model=List[schemas.PhoneNumberInfoResponse])
def get_all_phone_numbers(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    phone_numbers = db.query(model.PhoneNumber).all()
    if not phone_numbers:
        response.status_code = status.HTTP_404_NOT_FOUND
    return phone_numbers


@router.get("/{phone_number_id}", response_model=schemas.PhoneNumberInfoResponse)
def get_phone_number_by_id(
    phone_number_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    phone_number = (
        db.query(model.PhoneNumber)
        .filter(model.PhoneNumber.id == phone_number_id)
        .first()
    )
    if not phone_number:
        response.status_code = status.HTTP_404_NOT_FOUND
    return phone_number


@router.get("csv")
def get_phone_numbers_csv(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    # Query all phone numbers
    internal_numbers = db.query(model.InternalNumber).all()

    if not internal_numbers:
        response.status_code = status.HTTP_404_NOT_FOUND

    df = pd.DataFrame(
        [
            {
                "internal": pn.internal_number,
                "path": pn.path,
                "number": pn.phone_number.number,
                "phone_number_owner_name": pn.phone_number.phone_number_owner.name,
            }
            for pn in internal_numbers
        ]
    )

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=phone_numbers.csv"},
    )


@router.post("csv")
async def upload_phone_numbers(
    file: UploadFile = File(...), db: Session = Depends(util.get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a CSV file."
        )

    # Read the CSV file content
    contents = await file.read()
    csv_data = StringIO(contents.decode("utf-8"))

    # Load the CSV into a DataFrame
    try:
        df = pd.read_csv(csv_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")

    # Validate DataFrame columns
    required_columns = {"number", "phone_number_owner_name"}  # Adjust as needed
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail="CSV must contain columns: number, phone_number_owner_name",
        )

    # Insert data into the database
    for _, row in df.iterrows():
        phone_number_owner_id = 0

        new_phone_number_owner = model.PhoneNumberOwner(
            name=row["phone_number_owner_name"]
        )
        PhoneNumberOwner_exist = (
            db.query(model.PhoneNumberOwner)
            .filter(model.PhoneNumberOwner.name == new_phone_number_owner.name)
            .first()
        )

        if PhoneNumberOwner_exist:
            phone_number_owner_id = PhoneNumberOwner_exist.id
        else:
            db.add(new_phone_number_owner)
            db.commit()
            db.refresh(new_phone_number_owner)
            phone_number_owner_id = new_phone_number_owner.id
        db.query(model.PhoneNumberOwner)
        new_phone_number = model.PhoneNumber(
            number=row["number"], phone_number_owner_id=phone_number_owner_id
        )
        db.add(new_phone_number)
        db.commit()
        db.refresh(new_phone_number)
        new_internal_number = model.InternalNumber(
            internal_number=row["internal"],
            path=row["path"],
            phone_number_id=new_phone_number.id,
        )
        db.add(new_internal_number)
        db.commit()

    # Commit the session to save the changes

    return {"detail": "Phone numbers uploaded successfully"}


@router.put("update")
def update_phone_number(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    request: schemas.PhoneNumberUpdateRequest,
    db: Session = Depends(util.get_db),
):
    phone_number = (
        db.query(model.PhoneNumber).filter(model.PhoneNumber.id == request.id).first()
    )
    if not phone_number:
        response.status_code = status.HTTP_404_NOT_FOUND
    print(phone_number.number)
    phone_number.number = request.number
    phone_number.phone_number_owner_id = request.phone_number_owner_id

    db.commit()
    db.refresh(phone_number)
    return phone_number


@router.delete("/delete/{phone_number_id}")
def delete_phone_number_by_id(
    phone_number_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    phone_number = (
        db.query(model.PhoneNumber)
        .filter(model.PhoneNumber.id == phone_number_id)
        .first()
    )
    if not phone_number:
        response.status_code = status.HTTP_404_NOT_FOUND
    db.delete(phone_number)
    db.commit()
    return {"detail": "Item deleted successfully"}
