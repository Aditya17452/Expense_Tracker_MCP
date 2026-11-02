from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth.dependency import get_current_user
from app.db.session import get_db
from app.routes.errors import to_http
from app.schemas.expense_schema import ExpenseCreate, ExpenseOut, ExpenseSummary, ExpenseUpdate
from app.services import expense_service
from app.services.errors import ServiceError

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseOut, status_code=201)
def create_expense_route(data: ExpenseCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return expense_service.create_expense(data, db, user)


@router.get("", response_model=list[ExpenseOut])
def list_expenses_route(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return expense_service.list_expenses(db, user)


@router.get("/summary", response_model=ExpenseSummary)
def summary_route(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return expense_service.expense_summary(db, user)


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense_route(expense_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return expense_service.get_expense(expense_id, db, user)
    except ServiceError as exc:
        raise to_http(exc)


@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense_route(
    expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    try:
        return expense_service.update_expense(expense_id, data, db, user)
    except ServiceError as exc:
        raise to_http(exc)


@router.delete("/{expense_id}", status_code=204)
def delete_expense_route(expense_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        expense_service.delete_expense(expense_id, db, user)
    except ServiceError as exc:
        raise to_http(exc)
    return Response(status_code=204)
