# apps/middleware/routers/expenses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix='/expenses', tags=['Expenses'])


@router.post(
  '/', response_model=schemas.StandardResponse[schemas.ExpenseResponse], status_code=201
)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
  """Creates a new expense and links the owner, event, and participants."""

  db_event = (
    db.query(models.Event).filter(models.Event.uuid == expense.event_id).first()
  )
  if not db_event:
    raise HTTPException(status_code=404, detail='Event not found')

  db_owner = db.query(models.User).filter(models.User.uuid == expense.owner_id).first()
  if not db_owner:
    raise HTTPException(status_code=404, detail='Owner not found')

  expense_data = expense.model_dump(exclude={'participant_ids', 'owner_id', 'event_id'})

  db_expense = models.Expense(
    **expense_data, owner_id=db_owner.id, event_id=db_event.id
  )

  if expense.participant_ids:
    participants = (
      db.query(models.User).filter(models.User.uuid.in_(expense.participant_ids)).all()
    )
    db_expense.participants.extend(participants)

  db.add(db_expense)
  db.commit()
  db.refresh(db_expense)
  return schemas.success_response(data=db_expense, code=201)
