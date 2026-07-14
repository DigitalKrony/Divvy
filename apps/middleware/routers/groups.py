from typing import List
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas

router = APIRouter()


@router.post(
  '/', response_model=schemas.StandardResponse[schemas.GroupResponse], status_code=201
)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
  """
  Creates a new group in the database.
  """
  db_group = models.Group(**group.model_dump())
  db.add(db_group)
  db.commit()
  db.refresh(db_group)
  return schemas.success_response(data=db_group, code=201)


@router.post(
  '/{group_uuid}/members/{user_uuid}',
  response_model=schemas.StandardResponse[schemas.GroupResponse],
  status_code=201,
)
def add_user_to_group(group_uuid: str, user_uuid: str, db: Session = Depends(get_db)):
  """
  Links an existing user to an existing group.
  """
  group = db.query(models.Group).filter(models.Group.uuid == group_uuid).first()
  if not group:
    raise HTTPException(status_code=404, detail='Group not found')

  user = db.query(models.User).filter(models.User.uuid == user_uuid).first()
  if not user:
    raise HTTPException(status_code=404, detail='User not found')

  if user in group.members:
    raise HTTPException(
      status_code=400, detail='User is already a member of this group'
    )

  group.members.append(user)
  db.commit()
  db.refresh(group)
  return schemas.success_response(data=group, code=201)


@router.get(
  '/{group_uuid}/members',
  response_model=schemas.StandardResponse[List[schemas.UserResponse]],
  status_code=200,
)
def get_group_members(group_uuid: str, db: Session = Depends(get_db)):
  """
  Retrieves all users that are members of a specific group.
  """
  group = db.query(models.Group).filter(models.Group.uuid == group_uuid).first()
  if not group:
    raise HTTPException(status_code=404, detail='Group not found')
  return schemas.success_response(data=group.members, code=200)


@router.get(
  '/{group_uuid}/events',
  response_model=schemas.StandardResponse[List[schemas.EventResponse]],
  status_code=200,
)
def get_group_events(group_uuid: str, db: Session = Depends(get_db)):
  """
  Retrieves all events that are associated with a specific group.
  """
  group = db.query(models.Group).filter(models.Group.uuid == group_uuid).first()
  if not group:
    raise HTTPException(status_code=404, detail='Group not found')
  return schemas.success_response(data=group.events, code=200)
