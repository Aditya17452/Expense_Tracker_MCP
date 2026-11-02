"""MCP server that lets AI assistants (Claude Desktop, Cursor, etc.) manage expenses.

It reuses the same service layer and database as the REST API, and acts on behalf of
one user whose credentials are read from the environment:

    EXPENSE_USER_EMAIL, EXPENSE_USER_PASSWORD

Run with:  python mcp_server.py   (stdio transport)
"""

import os
from contextlib import contextmanager

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from app.core.config import DATABASE_URL  # noqa: F401  (loads .env)
from app.db.session import SessionLocal, create_tables
from app.schemas.expense_schema import ExpenseCreate, ExpenseOut, ExpenseUpdate
from app.services import expense_service
from app.services.errors import ServiceError
from app.services.user_service import authenticate_user

mcp = MCPServer("expense-tracker")


@contextmanager
def user_session():
    """Open a DB session and authenticate the configured user."""
    email = os.getenv("EXPENSE_USER_EMAIL")
    password = os.getenv("EXPENSE_USER_PASSWORD")
    if not email or not password:
        raise ToolError("Set EXPENSE_USER_EMAIL and EXPENSE_USER_PASSWORD for the MCP server")
    db = SessionLocal()
    try:
        yield db, authenticate_user(email, password, db)
    except ServiceError as exc:
        # Return a clear message (e.g. "Expense not found") to the AI client
        raise ToolError(str(exc)) from exc
    finally:
        db.close()


def _out(expense) -> dict:
    return ExpenseOut.model_validate(expense).model_dump(mode="json")


@mcp.tool()
def add_expense(title: str, amount: float) -> dict:
    """Record a new expense. `amount` must be greater than zero."""
    with user_session() as (db, user):
        return _out(expense_service.create_expense(ExpenseCreate(title=title, amount=amount), db, user))


@mcp.tool()
def list_expenses() -> list[dict]:
    """List all of the user's expenses, newest first."""
    with user_session() as (db, user):
        return [_out(e) for e in expense_service.list_expenses(db, user)]


@mcp.tool()
def get_expense(expense_id: int) -> dict:
    """Get one expense by its id."""
    with user_session() as (db, user):
        return _out(expense_service.get_expense(expense_id, db, user))


@mcp.tool()
def update_expense(expense_id: int, title: str, amount: float) -> dict:
    """Change the title and amount of an existing expense."""
    with user_session() as (db, user):
        data = ExpenseUpdate(title=title, amount=amount)
        return _out(expense_service.update_expense(expense_id, data, db, user))


@mcp.tool()
def delete_expense(expense_id: int) -> str:
    """Delete an expense by its id."""
    with user_session() as (db, user):
        expense_service.delete_expense(expense_id, db, user)
        return f"Expense {expense_id} deleted"


@mcp.tool()
def expense_summary() -> dict:
    """Return the number of expenses and the total amount spent."""
    with user_session() as (db, user):
        return expense_service.expense_summary(db, user)


if __name__ == "__main__":
    create_tables()
    mcp.run()
