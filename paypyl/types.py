from typing import Literal

ProductType = Literal["SERVICE", "DIGITAL", "PHYSICAL"]
PreferType = Literal["minimal", "representation"]
UpdateOp = Literal["add", "replace", "remove", "move", "copy", "test"]
PlanStatus = Literal["ACTIVE", "INACTIVE", "CREATED"]
TenureType = Literal["REGULAR", "TRIAL"]
IntervalUnit = Literal["DAY", "WEEK", "MONTH", "YEAR"]
PricingModel = Literal["TIERED", "VOLUME"]
SetupFeeFailureAction = Literal["CONTINUE", "CANCEL"]
Method = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "CONNECT"]
AddressType = Literal["SHIPPING", "PICKUP_IN_PERSON"]
PhoneType = Literal["HOME", "PAGER", "MOBILE", "FAX", "OTHER"]
SubscriptionStatus = Literal[
    "APPROVAL_PENDING", "APPROVED", "ACTIVE", "SUSPENDED", "CANCELLED", "EXPIRED"
]
LastPaymentStatus = Literal[
    "COMPLETED", "DECLINED", "PARTIALLY_REFUNDED", "PENDING", "REFUNDED"
]
FailedPaymentReason = Literal[
    "PAYMENT_DENIED",
    "INTERNAL_SERVER_ERROR",
    "PAYEE_ACCOUNT_RESTRICTED",
    "PAYER_ACCOUNT_RESTRICTED",
    "PAYER_CANNOT_PAY",
    "SENDING_LIMIT_EXCEEDED",
    "TRANSACTION_RECEIVING_LIMIT_EXCEEDED",
    "CURRENCY_MISMATCH",
]
