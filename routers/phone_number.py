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
    # current_user: Annotated[schemas.UserInfo, Depends(util.get_current_user)],
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
    db: Session = Depends(util.get_db),
):
    user_types = db.query(model.PhoneNumber).all()
    if not user_types:
        response.status_code = status.HTTP_404_NOT_FOUND
    return user_types


@router.get("/{user_type_id}", response_model=schemas.PhoneNumberInfoResponse)
def get_phone_number_by_id(
    user_type_id: int,
    response: Response,
    db: Session = Depends(util.get_db),
):
    user_type = (
        db.query(model.PhoneNumber).filter(model.PhoneNumber.id == user_type_id).first()
    )
    if not user_type:
        response.status_code = status.HTTP_404_NOT_FOUND
    return user_type


@router.get("csv")
def get_phone_numbers_csv(response: Response, db: Session = Depends(util.get_db)):
    # Query all phone numbers
    phone_numbers = db.query(model.PhoneNumber).all()

    if not phone_numbers:
        response.status_code = status.HTTP_404_NOT_FOUND

    df = pd.DataFrame(
        [
            {
                "number": pn.number,
                "phone_number_owner_id": pn.phone_number_owner_id,
            }
            for pn in phone_numbers
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
    required_columns = {"number", "phone_number_owner_id"}  # Adjust as needed
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail="CSV must contain columns: number, phone_number_owner_id",
        )

    # Insert data into the database
    for _, row in df.iterrows():
        new_phone_number = model.PhoneNumber(
            number=row["number"], phone_number_owner_id=row["phone_number_owner_id"]
        )
        db.add(new_phone_number)

    db.commit()  # Commit the session to save the changes

    return {"detail": "Phone numbers uploaded successfully"}


@router.put("update")
def update_phone_number(
    response: Response,
    request: schemas.PhoneNumberUpdateRequest,
    db: Session = Depends(util.get_db),
):
    user_type = db.query(model.PhoneNumber).filter(model.User.id == request.id).first()
    if not user_type:
        response.status_code = status.HTTP_404_NOT_FOUND
    user_type.number = request.number
    user_type.phone_number_owner_id = request.phone_number_owner_id

    db.commit()
    db.refresh(user_type)
    return user_type


@router.delete("/delete/{user_type_id}")
def delete_phone_number_by_id(
    user_type_id: int,
    response: Response,
    db: Session = Depends(util.get_db),
):
    user_type = (
        db.query(model.PhoneNumber).filter(model.PhoneNumber.id == user_type_id).first()
    )
    if not user_type:
        response.status_code = status.HTTP_404_NOT_FOUND
    db.delete(user_type)
    db.commit()
    return {"detail": "Item deleted successfully"}
