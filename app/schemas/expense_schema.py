from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1)
    amount: float = Field(gt=0)


class ExpenseUpdate(ExpenseCreate):
    pass


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: float
    created_at: datetime


class ExpenseSummary(BaseModel):
    count: int
    total: float
