from typing import Optional, TypeVar, Generic, List
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .types import *


class Link(BaseModel):
    href: str
    rel: str
    method: Optional[Method] = None


Links = List[Link]


class Resource(BaseModel):
    id: str | None = None
    create_time: datetime | None = Field(None, repr=False)
    update_time: datetime | None = Field(None, repr=False)
    links: Optional[Links] = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(extra="allow")


R = TypeVar("R")


class ResourceList(BaseModel, Generic[R]):
    __pydantic_extra__: dict[str, List[R]]
    total_items: int | None = None
    total_pages: int | None = None
    links: Optional[Links] = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(extra="allow")


class Money(BaseModel):
    currency_code: str
    value: str


class Frequency(BaseModel):
    interval_unit: IntervalUnit
    interval_count: int | None = None

    @classmethod
    def day(cls, count: int | None = None):
        return cls(interval_unit="DAY", interval_count=count)

    @classmethod
    def week(cls, count: int | None = None):
        return cls(interval_unit="WEEK", interval_count=count)

    @classmethod
    def month(cls, count: int | None = None):
        return cls(interval_unit="MONTH", interval_count=count)

    @classmethod
    def year(cls, count: int | None = None):
        return cls(interval_unit="YEAR", interval_count=count)


class PricingTier(BaseModel):
    starting_quantity: str
    ending_quantity: str | None = None
    amount: Money


class PricingScheme(BaseModel):
    version: int | None = None
    pricing_model: Optional[PricingModel] = None
    tiers: Optional[List[PricingTier]] = None
    fixed_price: Optional[Money] = Field(None)
    create_time: datetime | None = None
    update_time: datetime | None = None


class BillingCycle(BaseModel):
    tenure_type: TenureType
    sequence: int
    total_cycles: int | None = None
    pricing_scheme: Optional[PricingScheme] = None
    frequency: Frequency


class CycleExecution(BaseModel):
    tenure_type: TenureType
    sequence: int
    cycles_completed: int
    cycles_remaining: int | None = None
    current_pricing_scheme_version: int | None = None
    total_cycles: int | None = None


class PaymentPreferences(BaseModel):
    auto_bill_outstanding: bool | None = None
    setup_fee_failure_action: Optional[SetupFeeFailureAction] = None
    payment_failure_threshold: int | None = None
    setup_fee: Optional[Money] = None


class Taxes(BaseModel):
    percentage: str
    inclusive: bool | None = None


class PlanOverride(BaseModel):
    billing_cycles: Optional[List[BillingCycle]] = Field(None, repr=False)
    payment_preferences: PaymentPreferences = Field(default_factory=PaymentPreferences)
    taxes: Optional[Taxes] = Field(None, repr=False)


class Name(BaseModel):
    given_name: str
    surname: str


class PhoneNumber(BaseModel):
    national_number: str


class Phone(BaseModel):
    phone_type: Optional[PhoneType] = None
    phone_number: PhoneNumber


class Address(BaseModel):
    address_line_1: str | None = None
    address_line_2: str | None = None
    admin_area_2: str | None = None
    admin_area_1: str | None = None
    postal_code: str | None = None
    country_code: str


class ShippingDetail(BaseModel):
    type: Optional[AddressType] = None
    name: Optional[Name] = None
    address: Optional[Address] = None


class Card(BaseModel):
    name: str | None = None
    number: str
    security_code : str | None = None
    expiry: str
    billing_address: Optional[Address] = None


class PaymentSource(BaseModel):
    card: Optional[Card] = None


class Subscriber(BaseModel):
    email_address: str | None = None
    name: Optional[Name] = Field(None, repr=None)
    phone: Optional[Phone] = None
    shipping_address: Optional[ShippingDetail] = Field(None, repr=False)
    payment_source: Optional[PaymentSource] = Field(None, repr=False)


class LastPayment(BaseModel):
    status: Optional[LastPaymentStatus] = None
    amount: Money
    time: datetime


class FailedPayment(BaseModel):
    reason_code: Optional[FailedPaymentReason] = None
    amount: Money
    time: datetime
    next_payment_retry_time: datetime | None = None


class BillingInfo(BaseModel):
    cycle_executions: Optional[List[CycleExecution]] = None
    failed_payments_count: int
    outstanding_balance: Money
    last_payment: Optional[LastPayment] = None
    next_billing_time: datetime | None = None
    final_payment_time: datetime | None = None
    last_failed_payment: Optional[FailedPayment] = None


class EventType(BaseModel):
    name: str
    description: str | None = None
    status: Optional[str] = None
    resource_versions: Optional[List[str]] = None
    links: Optional[Links] = None
