from model.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Time
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(999))
    password = Column(String(999))
    fname = Column(String(999))
    lname = Column(String(999))
    email = Column(String(999))
    user_type_id = Column(Integer, ForeignKey("user_types.id"))
    type = relationship("UserType", back_populates="type_users")

    tickets = relationship("Ticket", back_populates="user")


class UserType(Base):

    __tablename__ = "user_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(999))

    type_users = relationship("User", back_populates="type")


class InternalNumber(Base):

    __tablename__ = "internal_numbers"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(999))
    path = Column(String(999))

    phone_number_id = Column(Integer, ForeignKey("phone_numbers.id"))
    phone_number = relationship("PhoneNumber", back_populates="internal_number_s")


class PhoneNumber(Base):

    __tablename__ = "phone_numbers"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(999))

    phone_number_owner_id = Column(Integer, ForeignKey("phone_number_owners.id"))
    phone_number_owner = relationship(
        "PhoneNumberOwner", back_populates="phone_numbers"
    )

    internal_number_s = relationship("InternalNumber", back_populates="phone_number")


class PhoneNumberOwner(Base):

    __tablename__ = "phone_number_owners"
    id = Column(Integer, primary_key=True, index=True)
    fname = Column(String(999))
    lname = Column(String(999))
    email = Column(String(999))

    phone_numbers = relationship("PhoneNumber", back_populates="phone_number_owner")


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(999))

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tickets")
