from typing import Literal
from datetime import timedelta

from pydantic import BaseModel

from .types import *
from .resources import *
from .definitions import *


class TokenResult(BaseModel):
    scope: str
    access_token: str
    token_type: Literal["Bearer"]
    app_id: str
    expires_in: timedelta
    nonce: str


class WebhookSignatureResponse(BaseModel):
    verification_status: Literal["SUCCESS", "FAILURE"]
