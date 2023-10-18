from typing import Optional

from pydantic import Field

from .types import *
from .definitions import *


class Product(Resource):
    name: str
    description: str | None = Field(None, repr=False)
    type: ProductType | None = None
    category: str | None = None
    image_url: str | None = Field(None, repr=False)
    home_url: str | None = Field(None, repr=False)


class Plan(Resource):
    product_id: str
    name: str
    status: PlanStatus | None = None
    description: str | None = Field(None, repr=False)
    billing_cycles: Optional[List[BillingCycle]] = Field(None, repr=False)
    quantity_supported: bool | None = Field(None, repr=False)
    payment_preferences: PaymentPreferences = Field(default_factory=PaymentPreferences, repr=False)
    taxes: Optional[Taxes] = Field(None, repr=False)


class Subscription(Resource):
    status: Optional[SubscriptionStatus] = None
    status_change_note: str | None = Field(None, repr=False)
    status_update_time: datetime | None = Field(None, repr=False)
    plan_id: str | None = None
    quantity: str | None = Field(None, repr=False)
    plan_overridden: bool | None = None
    start_time: datetime | None = Field(None, repr=False)
    shipping_amount: Money | None = Field(None, repr=False)
    subscriber: Subscriber | None = Field(None, repr=False)
    billing_info: BillingInfo | None = Field(None, repr=False)
    auto_renewal: bool | None = Field(None, repr=False)
    custom_id: str | None = None
    plan: Optional[PlanOverride] = Field(None, repr=False)


class Webhook(BaseModel):
    id: str | None = None
    url: str
    event_types: List[EventType]
    links: List[Link] | None = None


class Event(BaseModel):
    id: str
    create_time: datetime = Field(repr=False)
    resource_type: str
    event_version: str = Field(repr=False)
    event_type: str
    summary: str = Field(repr=False)
    resource_version: str = Field(repr=False)
    resource: Resource = Field(repr=False)
    links: Optional[Links] = Field(None, repr=False)

    model_config = ConfigDict(extra="allow")
