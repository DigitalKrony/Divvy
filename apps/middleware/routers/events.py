from typing import List
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas

router = APIRouter()


@router.post(
  '/', response_model=schemas.StandardResponse[schemas.EventResponse], status_code=201
)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
  """Creates a new event."""
  db_event = models.Event(**event.model_dump())

  db.add(db_event)
  db.commit()
  db.refresh(db_event)

  return schemas.success_response(data=db_event, code=201)


@router.get(
  '/{event_uuid}',
  response_model=schemas.StandardResponse[schemas.EventResponse],
  status_code=200,
)
def get_event(event_uuid: str, db: Session = Depends(get_db)):
  """Retrieves a specific event by its UUID."""

  event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()

  if not event:
    raise HTTPException(status_code=404, detail='Event not found')

  return schemas.success_response(data=event, code=200)


@router.post(
  '/{event_uuid}/users/{user_uuid}',
  response_model=schemas.StandardResponse[schemas.EventResponse],
  status_code=201,
)
def add_user_to_event(event_uuid: str, user_uuid: str, db: Session = Depends(get_db)):
  """Registers a user for an event."""
  event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()
  user = db.query(models.User).filter(models.User.uuid == user_uuid).first()

  if not event or not user:
    raise HTTPException(status_code=404, detail='Event or User not found')

  if user in event.users:
    raise HTTPException(
      status_code=400, detail='User is already registered for this event'
    )

  event.users.append(user)
  db.commit()
  db.refresh(event)

  return schemas.success_response(data=event, code=201)


@router.get(
  '/{event_uuid}/users',
  response_model=schemas.StandardResponse[List[schemas.UserResponse]],
  status_code=200,
)
def get_event_users(event_uuid: str, db: Session = Depends(get_db)):
  """Retrieves all individual users registered for a specific event."""
  event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()

  if not event:
    raise HTTPException(status_code=404, detail='Event not found')

  return schemas.success_response(data=event.users, code=200)


@router.post(
  '/{event_uuid}/groups/{group_uuid}',
  response_model=schemas.StandardResponse[schemas.EventResponse],
  status_code=201,
)
def add_group_to_event(event_uuid: str, group_uuid: str, db: Session = Depends(get_db)):
  """Attaches an entire group to an event."""
  event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()
  group = db.query(models.Group).filter(models.Group.uuid == group_uuid).first()

  if not event or not group:
    raise HTTPException(status_code=404, detail='Event or Group not found')

  if group in event.groups:
    raise HTTPException(
      status_code=400, detail='Group is already attached to this event'
    )

  event.groups.append(group)
  db.commit()
  db.refresh(event)

  return schemas.success_response(data=event, code=201)


@router.get(
  '/{event_uuid}/groups',
  response_model=schemas.StandardResponse[List[schemas.GroupResponse]],
  status_code=200,
)
def get_event_groups(event_uuid: str, db: Session = Depends(get_db)):
  """Retrieves all groups registered for a specific event."""
  event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()

  if not event:
    raise HTTPException(status_code=404, detail='Event not found')

  return schemas.success_response(data=event.groups, code=200)
