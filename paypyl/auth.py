from typing import TYPE_CHECKING, Literal, Optional
from datetime import datetime
from dataclasses import dataclass
from threading import Thread

from requests.auth import AuthBase

if TYPE_CHECKING:
    from requests.models import PreparedRequest

    from .client import Client


__all__ = ["Auth", "AuthToken"]


@dataclass
class AuthToken:
    type: Literal["Bearer"]
    value: str
    expire_at: datetime

    def expired(self, timestamp: datetime) -> bool:
        return timestamp > self.expire_at


class Auth(AuthBase):
    token: Optional[AuthToken] = None
    client: "Client"
    thread: Optional[Thread] = None

    def __init__(self, client: "Client"):
        self.client = client
        self.token = None
    
    def _update_token(self, timestamp: datetime, **kwargs):
        result = self.client.request_access_token(**kwargs)
        self.token = AuthToken(
            type=result.token_type,
            value=result.access_token,
            expire_at=timestamp + result.expires_in
        )

    def update_token(self, timestamp: datetime, **kwargs) -> str:
        if self.thread is None:
            self.thread = Thread(target=self._update_token, args=(timestamp,), kwargs=kwargs)
            self.thread.start()

        self.thread = self.thread.join()

        return self.token.value

    def __call__(self, r: "PreparedRequest") -> "PreparedRequest":
        access_token = self.client.access_token
        token_type = "Bearer"

        if access_token is None:
            timestamp = datetime.now()
            if self.token is None or self.token.expired(timestamp):
                access_token = self.update_token(timestamp)
            else:
                access_token = self.token.value
            token_type = self.token.type

        r.headers["Authorization"] = f"{token_type} {access_token}"
        return r
