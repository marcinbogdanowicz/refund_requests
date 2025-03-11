from enum import StrEnum


class RefundStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RefundReason(StrEnum):
    WRONG_PRODUCT = "Wrong product"
    PRODUCT_DAMAGED = "Product damaged"
    PRODUCT_DEFECTIVE = "Product defective"
    OTHER = "Other"

    @classmethod
    def as_choices(cls):
        return [(choice.value, choice.value) for choice in cls]
