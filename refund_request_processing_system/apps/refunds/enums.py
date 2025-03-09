from enum import StrEnum


class RefundStatus(StrEnum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
