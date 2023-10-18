from typing import Annotated, TYPE_CHECKING
from logging import getLogger
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Header, Body
from fastapi.exceptions import HTTPException

from paypyl.resources import Event

if TYPE_CHECKING:
    from paypyl.client import Client as PayPyl


logger = getLogger()
app = FastAPI(on_startup=[load_dotenv])


def get_paypyl():
    from paypyl import Client

    return Client()


@app.post("/webhook")
def handle_webhook_event_notification(
    paypyl: Annotated["PayPyl", Depends(get_paypyl)],
    paypal_auth_algo: Annotated[str, Header()],
    paypal_cert_url: Annotated[str, Header()],
    paypal_transmission_id: Annotated[str, Header()],
    paypal_transmission_sig: Annotated[str, Header()],
    paypal_transmission_time: Annotated[datetime, Header()],
    event: Annotated[Event, Body()],
):
    signature = {
        "auth_algo": paypal_auth_algo,
        "cert_url": paypal_cert_url,
        "transmission_id": paypal_transmission_id,
        "transmission_sig": paypal_transmission_sig,
        "transmission_time": paypal_transmission_time,
    }

    webhook_id = "1SV15366HH1953807"
    try:
        event = paypyl.verify_event(webhook_id, signature, event)
        print(event.summary, repr(event))
    except AssertionError:
        print("Invalid signature")
        # raise HTTPException(400, "Invalid signature")
