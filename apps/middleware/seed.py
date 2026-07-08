from sqlalchemy.orm import Session
from database import SessionLocal
import os
import json
import models

def seed_database(db: Session):
    """Populates the database with initial fake data for frontend development."""
    
    if os.getenv("ENVIRONMENT") != "development":
        print("Not in development mode. Skipping seed.")
        return

    print("Development mode detected. Seeding database...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, ".mock/db.json")

    try:
        with open(json_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: Could not find {json_path}. Please create it first!")
        return

    db_users = []
    for user_info in data.get("users", []):
        existing = db.query(models.User).filter(models.User.email_address == user_info["email_address"]).first()
        if not existing:
            new_user = models.User(**user_info)
            db.add(new_user)
            db_users.append(new_user)
        else:
            db_users.append(existing)
            
    db.commit()

    db_groups = []
    for group_info in data.get("groups", []):
        existing = db.query(models.Group).filter(models.Group.name == group_info["name"]).first()
        if not existing:
            new_group = models.Group(**group_info)
            db.add(new_group)
            db_groups.append(new_group)
        else:
            db_groups.append(existing)

    db.commit()

    for event_info in data.get("events", []):
        existing = db.query(models.Event).filter(models.Event.title == event_info["title"]).first()
        if not existing:
            new_event = models.Event(**event_info)
            # Attach a random group for relationships
            new_event.groups.append(db_groups[0])
            db.add(new_event)

    db.commit()
    print("Database successfully seeded!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()