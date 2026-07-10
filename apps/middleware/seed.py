from sqlalchemy.orm import Session
from database import SessionLocal
from dateutil import parser
from sqlalchemy import text
import os
import json
import models

def seed_database(db: Session):
    """Populates the database with initial fake data from a JSON file."""
    
    current_env = os.getenv("ENVIRONMENT", "production").lower()
    if current_env != "development":
        print(f"Server is in '{current_env}' mode. Skipping seed for safety.")
        return

    print("Wiping existing data for a clean slate...")
    db.execute(text("TRUNCATE TABLE users, groups, events CASCADE;"))
    db.commit()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, ".mock/db.json")

    try:
        with open(json_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: Could not find {json_path}. Please create it first!")
        return

    user_map = {}
    group_map = {}
    event_map = {}

    print("Seeding Users...")
    for user_info in data.get("users", []):
        address_data = user_info.pop("address", None)
        pay_accounts = user_info.pop("pay_accounts", [])
        
        if "uuid" in user_info:
            user_info["uuid"] = user_info.pop("uuid")
            
        new_user = models.User(**user_info)
        
        if address_data and hasattr(models, "Address"):
            address_data.pop("id", None) 
            new_user.address = models.Address(**address_data)
            
        db.add(new_user)
        db.flush() 
        user_map[new_user.uuid] = new_user

    print("Seeding Groups...")
    for group_info in data.get("groups", []):
        rel_users = group_info.pop("users", [])
        rel_events = group_info.pop("events", [])
        
        if "uuid" in group_info:
            group_info["uuid"] = group_info.pop("uuid")
            
        new_group = models.Group(**group_info)
        db.add(new_group)
        db.flush()
        group_map[new_group.uuid] = new_group

    print("Seeding Events...")
    for event_info in data.get("events", []):
        rel_users = event_info.pop("users", [])
        rel_groups = event_info.pop("groups", [])
        
        if "uuid" in event_info:
            event_info["uuid"] = event_info.pop("uuid")
            
        if "start_date" in event_info:
            clean_date = event_info["start_date"].split(" (")[0]
            event_info["start_date"] = parser.parse(clean_date)
            
        if "end_date" in event_info:
            clean_date = event_info["end_date"].split(" (")[0]
            event_info["end_date"] = parser.parse(clean_date)
            
        new_event = models.Event(**event_info)
        db.add(new_event)
        db.flush()
        event_map[new_event.uuid] = new_event

    print("Linking Relationships...")
    
    for group_info in data.get("groups", []):
        group = group_map.get(group_info.get("uuid"))
        if group:
            for u_uuid in group_info.get("users", []):
                if u_uuid in user_map and user_map[u_uuid] not in group.users:
                    group.users.append(user_map[u_uuid])

    for event_info in data.get("events", []):
        event = event_map.get(event_info.get("uuid"))
        if event:
            for u_uuid in event_info.get("users", []):
                if u_uuid in user_map and user_map[u_uuid] not in event.users:
                    event.users.append(user_map[u_uuid])
            for g_uuid in event_info.get("groups", []):
                if g_uuid in group_map and group_map[g_uuid] not in event.groups:
                    event.groups.append(group_map[g_uuid])

    db.commit()
    print("Database successfully seeded from db.json!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()