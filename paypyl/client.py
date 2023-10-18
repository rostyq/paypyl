from typing import Any, Mapping, Generator, Type, List
from os import environ
from urllib.parse import urljoin
from functools import lru_cache

from pydantic import TypeAdapter
from requests import Session, Request

from .update import Update
from .auth import Auth
from .constants import *
from .types import *
from .resources import *
from .definitions import *
from .responses import *


__all__ = ["Client"]


@lru_cache
def _endpoint(base: str, path: str):
    return urljoin(base, path)


class Client:
    session: Session
    auth: Auth
    url: str = LIVE_URL
    client_id: str | None = None
    client_secret: str | None = None
    access_token: str | None = None

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        sandbox: bool | None = None,
    ):
        self.session = Session()
        self.session.auth = Auth(self)
        self.session.headers.update({"Content-Type": "application/json"})

        self.client_id = client_id or environ.get(CLIENT_ID_KEY)
        self.client_secret = client_secret or environ.get(CLIENT_SECRET_KEY)
        self.access_token = None

        if sandbox is None:
            sandbox = environ.get(MODE_KEY) == "sandbox"

        if sandbox:
            self.url = SANDBOX_URL

    def __truediv__(self, other: str):
        assert isinstance(other, str) and other, "other must be a non-empty string."
        return _endpoint(self.url, other)

    def request_access_token(
        self, client_id: str | None = None, client_secret: str | None = None
    ):
        url = self / "v1/oauth2/token"

        client_id = client_id or self.client_id
        client_secret = client_secret or self.client_secret
        auth = (client_id, client_secret)

        data = {"grant_type": "client_credentials"}

        request = Request(url=url, method="POST", auth=auth, data=data)
        request = request.prepare()
        response = self.session.send(request)
        response.raise_for_status()

        return TokenResult.model_validate_json(response.content)

    def _create(
        self,
        endpoint: str,
        /,
        resource: R,
        *,
        prefer: PreferType | None = None,
        request_id: str | None = None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> R:
        url = self / endpoint

        headers = {}

        if extra_headers is not None:
            headers.update(extra_headers)

        if prefer is not None:
            headers["Prefer"] = f"return={prefer}"

        if request_id is not None:
            headers["PayPal-Request-Id"] = request_id

        data = resource.model_dump_json(
            exclude=["create_time", "update_time"], exclude_none=True
        )

        response = self.session.post(url=url, data=data, headers=headers)
        response.raise_for_status()

        return resource.__class__.model_validate_json(response.content)

    def _delete(self, endpoint: str, resource_id: str, /) -> None:
        url = self._resource(endpoint, resource_id)
        self.session.delete(url=url).raise_for_status()

    def _list(
        self,
        endpoint: str,
        *,
        page_size: int | None = None,
        page: int | None = None,
        total_required: bool | None = None,
        convert: Type[R] = Resource,
        **kwargs,
    ):
        url = self / endpoint
        name = endpoint.split("/")[-1]

        params = {
            "page_size": page_size,
            "page": page,
            "total_required": total_required,
            **kwargs,
        }

        response = self.session.get(url=url, params=params)
        response.raise_for_status()

        result = ResourceList[convert].model_validate_json(response.content)

        # monkeypatch validation
        setattr(
            result,
            name,
            list(map(convert.model_validate, getattr(result, name))),
        )

        return result

    def _iter(
        self,
        endpoint: str,
        *,
        page_size: int = 10,
        start_page: int = 1,
        convert: Type[R] = Resource,
    ) -> Generator[R, None, None]:
        name = endpoint.split("/")[-1]
        result = self._list(
            endpoint,
            page_size=page_size,
            page=start_page,
            total_required=True,
            convert=convert,
        )
        yield from getattr(result, name)

        current_page, total_pages = start_page, result.total_pages

        while current_page < total_pages:
            result = self._list(page_size=page_size, page=current_page, convert=convert)
            yield from getattr(result, name)
            current_page += 1

    def _resource(self, endpoint: str, resource_id: str, /):
        return (self / endpoint) + "/" + resource_id

    def _action(self, endpoint: str, resource_id: str, action: str, /):
        return self._resource(endpoint, resource_id) + "/" + action

    def _details(
        self,
        endpoint: str,
        /,
        resource_id: str,
        *,
        convert: Type[R] = Resource,
        **kwargs,
    ) -> R:
        r = self.session.get(url=self._resource(endpoint, resource_id), **kwargs)
        r.raise_for_status()
        return convert.model_validate_json(r.content)

    def _update(self, endpoint: str, /, resource_id: str, ops: List[Update]):
        data = TypeAdapter(List[Update]).dump_json(ops, exclude_none=True)
        response = self.session.patch(
            url=self._resource(endpoint, resource_id), data=data
        )
        response.raise_for_status()

    def create_product(
        self,
        data: Product,
        *,
        prefer: PreferType | None = None,
        request_id: str | None = None,
    ):
        return self._create(
            "v1/catalogs/products", resource=data, prefer=prefer, request_id=request_id
        )

    def list_products(
        self,
        *,
        page_size: int | None = None,
        page: int | None = None,
        total_required: bool | None = None,
    ) -> ResourceList[Product]:
        return self._list(
            "v1/catalogs/products",
            page_size=page_size,
            page=page,
            total_required=total_required,
        )

    def iter_products(self, *, page_size: int = 10, start_page: int = 1):
        yield from self._iter(
            "v1/catalogs/products",
            page_size=page_size,
            start_page=start_page,
            convert=Product,
        )

    def product_details(self, product_id: str, /):
        return self._details("v1/catalogs/products", product_id, convert=Product)

    def update_product(self, product_id: str, /, ops: list[Update]):
        self._update("v1/catalogs/products", product_id, ops)

    def create_plan(
        self,
        data: Plan,
        *,
        prefer: PreferType | None = None,
        request_id: str | None = None,
    ):
        return self._create(
            "v1/billing/plans", resource=data, prefer=prefer, request_id=request_id
        )

    def list_plans(
        self,
        *,
        page_size: int | None = None,
        page: int | None = None,
        total_required: bool | None = None,
    ) -> ResourceList[Plan]:
        return self._list(
            "v1/billing/plans",
            page_size=page_size,
            page=page,
            total_required=total_required,
        )

    def iter_plans(self, *, page_size: int = 10, start_page: int = 1):
        yield from self._iter(
            "v1/billing/plans",
            page_size=page_size,
            start_page=start_page,
            convert=Plan,
        )

    def plan_details(self, plan_id: str, /):
        return self._details("v1/billing/plans", plan_id, convert=Plan)

    def update_plan(self, product_id: str, /, ops: list[Update]):
        self._update("v1/billing/plans", product_id, ops)

    def activate_plan(self, plan_id: str, /):
        url = self._action("v1/billing/plans", plan_id, "activate")
        self.session.post(url=url).raise_for_status()

    def deactivate_plan(self, plan_id: str, /):
        url = self._action("v1/billing/plans", plan_id, "deactivate")
        self.session.post(url=url).raise_for_status()

    def create_subscription(
        self,
        data: Subscription,
        *,
        prefer: PreferType | None = None,
        request_id: str | None = None,
    ):
        return self._create(
            "v1/billing/subscriptions",
            resource=data,
            prefer=prefer,
            request_id=request_id,
        )

    def subscription_details(
        self,
        subscription_id: str,
        /,
        fields: Optional[List[Literal["plan", "last_failed_payment"]]] = None,
    ):
        params = None
        if fields is not None:
            params = {"fields": ",".join(fields)}

        return self._details(
            "v1/billing/subscriptions",
            subscription_id,
            convert=Subscription,
            params=params,
        )

    def activate_subscription(self, subscription_id: str, /):
        url = self._action("v1/billing/subscriptions", subscription_id, "activate")
        self.session.post(url=url).raise_for_status()

    def suspend_subscription(self, subscription_id: str, /):
        url = self._action("v1/billing/subscriptions", subscription_id, "suspend")
        self.session.post(url=url).raise_for_status()

    def cancel_subscription(self, subscription_id: str, /):
        url = self._action("v1/billing/subscriptions", subscription_id, "cancel")
        self.session.post(url=url).raise_for_status()

    def list_webhooks(
        self,
        *,
        anchor_type: Optional[Literal["APPLICATION", "ACCOUNT"]] = None,
    ) -> list[Webhook]:
        result = self._list(
            "v1/notifications/webhooks", convert=Webhook, anchor_type=anchor_type
        )
        return result.webhooks

    def create_webhook(self, data: Webhook):
        return self._create("v1/notifications/webhooks", resource=data)

    def delete_webhook(self, webhook_id: str, /):
        self._delete("v1/notifications/webhooks", webhook_id)

    def verify_event(
        self,
        /,
        webhook_id: str,
        signature: WebhookSignature | Mapping[str, Any],
        event: Event | Mapping[str, Any],
        *,
        dry_run: bool = False,
    ) -> Event:
        if not isinstance(signature, WebhookSignature):
            signature = WebhookSignature.model_validate(signature)

        if not isinstance(event, Event):
            event = Event.model_validate(event)

        if not dry_run:
            payload = {
                "webhook_id": webhook_id,
                "webhook_event": event.model_dump(
                    mode="json",
                    include=[
                        "id",
                        "create_time",
                        "resource_type",
                        "event_type",
                        "summary",
                        "resource",
                    ],
                ),
                **signature.model_dump(mode="json", exclude_none=True),
            }
            from pprint import pprint

            pprint(payload)

            url = self / "v1/notifications/verify-webhook-signature"
            response = self.session.post(url=url, json=payload)
            response.raise_for_status()

            result = WebhookSignatureResponse.model_validate_json(response.content)
            status = result.verification_status

            assert status == "SUCCESS", status

        return event

    def __del__(self):
        self.session.close()
