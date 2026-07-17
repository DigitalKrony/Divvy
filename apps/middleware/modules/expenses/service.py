from sqlalchemy.orm import Session

from . import models
from . import schemas
from ..users.models import User
from ..events.models import Event


def get_event_by_uuid(db: Session, event_uuid: str):
  """Helper to validate an event exists."""
  return db.query(Event).filter(Event.uuid == event_uuid).first()


def get_user_by_uuid(db: Session, user_uuid: str):
  """Helper to validate a user exists."""
  return db.query(User).filter(User.uuid == user_uuid).first()


def create_expense(
  db: Session,
  expense: schemas.ExpenseCreate,
  db_owner: User,
  db_event: Event,
):
  """Creates the expense and links all participants in the database."""
  # Exclude the relational IDs from the raw dump
  expense_data = expense.model_dump(exclude={'participant_ids', 'owner_id', 'event_id'})

  # Create the expense using the actual internal database IDs
  db_expense = models.Expense(
    **expense_data, owner_id=db_owner.id, event_id=db_event.id
  )

  # If there are participants, fetch them and build the many-to-many relation
  if expense.participant_ids:
    participants = (
      db.query(models.User).filter(User.uuid.in_(expense.participant_ids)).all()
    )
    db_expense.participants.extend(participants)

  db.add(db_expense)
  db.commit()
  db.refresh(db_expense)

  return db_expense
