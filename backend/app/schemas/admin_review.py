from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


DocumentReviewStatus = Literal['verified', 'rejected']


class DriverDocumentReviewRequest(BaseModel):
    status: DocumentReviewStatus
    review_note: str | None = Field(default=None, max_length=500)

    @model_validator(mode='after')
    def rejected_documents_need_a_reason(self) -> 'DriverDocumentReviewRequest':
        if self.status == 'rejected' and not (self.review_note or '').strip():
            raise ValueError('Provide a review note when rejecting a document.')
        return self


class DriverDocumentReviewResponse(BaseModel):
    driver_id: int
    document_type: str
    document_status: str
    vehicle_verification_status: str
    reviewed_at: datetime | None
    review_note: str | None
