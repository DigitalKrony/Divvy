from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import schemas as global_schemas
from . import schemas as expense_schemas
from ..groups import schemas as group_schema  # noqa: F401
from ..users import schemas as user_schema  # noqa: F401
from ..events import schemas as event_schema  # noqa: F401
from . import service as crud

router = APIRouter(prefix='/expenses', tags=['Expenses'])


@router.post(
  '/',
  response_model=global_schemas.StandardResponse[expense_schemas.ExpenseResponse],
  status_code=201,
)
def create_expense(
  expense: expense_schemas.ExpenseCreate, db: Session = Depends(get_db)
):
  """Creates a new expense and links the owner, event, and participants."""

  db_event = crud.get_event_by_uuid(db, event_uuid=expense.event_id)
  if not db_event:
    raise HTTPException(status_code=404, detail='Event not found')

  db_owner = crud.get_user_by_uuid(db, user_uuid=expense.owner_id)
  if not db_owner:
    raise HTTPException(status_code=404, detail='Owner not found')

  db_expense = crud.create_expense(
    db=db, expense=expense, db_owner=db_owner, db_event=db_event
  )

  return global_schemas.success_response(data=db_expense, code=201)
