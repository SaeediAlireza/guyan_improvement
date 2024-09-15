from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from model import model, schemas
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy import update

from util import util


router = APIRouter(tags=["ticket"], prefix="/tickets")


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_ticket(
    request: schemas.TicketAddRequest,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    new_ticket = model.Ticket(
        description=request.description,
        user_id=request.user_id,
    )
    Ticket_exist = (
        db.query(model.Ticket)
        .filter(model.Ticket.description == new_ticket.description)
        .first()
    )

    if Ticket_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ticket exists"
        )
    else:
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return new_ticket


@router.get("/all", response_model=List[schemas.TicketInfoResponse])
def get_all_tickets(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    Tickets = db.query(model.Ticket).all()
    if not Tickets:
        response.status_code = status.HTTP_404_NOT_FOUND
    return Tickets


@router.get("/{ticket_id}", response_model=schemas.TicketInfoResponse)
def get_ticket_by_id(
    ticket_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):

    Ticket = db.query(model.Ticket).filter(model.Ticket.id == ticket_id).first()

    if not Ticket:
        response.status_code = status.HTTP_404_NOT_FOUND
    return Ticket


@router.get("/user-ticket/{user_id}", response_model=schemas.TicketInfoResponse)
def get_ticket_by_user_id(
    user_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):

    Ticket = db.query(model.Ticket).filter(model.Ticket.user_id == user_id).first()

    if not Ticket:
        response.status_code = status.HTTP_404_NOT_FOUND
    return Ticket


@router.get(
    "/all-user-tickets/{user_id}", response_model=List[schemas.TicketInfoResponse]
)
def get_all_ticket_by_user_id(
    user_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):

    Tickets = db.query(model.Ticket).filter(model.Ticket.user_id == user_id).all()

    if not Tickets:
        response.status_code = status.HTTP_404_NOT_FOUND
    return Tickets


@router.put("update")
def update_ticket(
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    request: schemas.TicketUpdateRequest,
    db: Session = Depends(util.get_db),
):
    Ticket = db.query(model.Ticket).filter(model.Ticket.id == request.id).first()
    if not Ticket:
        response.status_code = status.HTTP_404_NOT_FOUND
    Ticket.description = request.description
    Ticket.user_id = request.user_id
    db.commit()
    db.refresh(Ticket)
    return Ticket


@router.delete("/delete/{Ticket_id}")
def delete_ticket_by_id(
    Ticket_id: int,
    response: Response,
    current_user: Annotated[schemas.UserInfoResponse, Depends(util.get_current_user)],
    db: Session = Depends(util.get_db),
):
    Ticket = db.query(model.Ticket).filter(model.Ticket.id == Ticket_id).first()
    if not Ticket:
        response.status_code = status.HTTP_404_NOT_FOUND
    db.delete(Ticket)
    db.commit()
    return {"detail": "Item deleted successfully"}
