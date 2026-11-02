from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense_schema import ExpenseCreate, ExpenseUpdate
from app.services.errors import NotFoundError, PermissionDeniedError


def create_expense(data: ExpenseCreate, db: Session, user: User) -> Expense:
    expense = Expense(
        title=data.title,
        amount=data.amount,
        created_at=datetime.now(timezone.utc),
        owner_id=user.id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(db: Session, user: User) -> list[Expense]:
    return (
        db.query(Expense)
        .filter(Expense.owner_id == user.id)
        .order_by(Expense.created_at.desc())
        .all()
    )


def get_expense(expense_id: int, db: Session, user: User) -> Expense:
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise NotFoundError("Expense not found")
    if expense.owner_id != user.id:
        raise PermissionDeniedError("You are not allowed to access this expense")
    return expense


def update_expense(expense_id: int, data: ExpenseUpdate, db: Session, user: User) -> Expense:
    expense = get_expense(expense_id, db, user)
    expense.title = data.title
    expense.amount = data.amount
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(expense_id: int, db: Session, user: User) -> None:
    expense = get_expense(expense_id, db, user)
    db.delete(expense)
    db.commit()


def expense_summary(db: Session, user: User) -> dict:
    count, total = (
        db.query(func.count(Expense.id), func.coalesce(func.sum(Expense.amount), 0.0))
        .filter(Expense.owner_id == user.id)
        .one()
    )
    return {"count": count, "total": round(float(total), 2)}
