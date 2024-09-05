from fastapi import FastAPI
import routers
from model import database, model
import ssl

import routers.authentication

import routers.internal_number
import routers.phone_number
import routers.phone_number_owner
import routers.ticket
import routers.user
import routers.user_type
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain("./cert.pem", keyfile="./key.pem")


model.Base.metadata.create_all(database.engine)

app.include_router(routers.authentication.router)

app.include_router(routers.user_type.router)
app.include_router(routers.user.router)
app.include_router(routers.ticket.router)
app.include_router(routers.phone_number_owner.router)
app.include_router(routers.phone_number.router)
app.include_router(routers.internal_number.router)
