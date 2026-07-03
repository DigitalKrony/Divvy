from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import models
from database import engine, get_db
from routers import items

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Divvy App v0.0.1")

app.include_router(items.router, prefix="/items", tags=["Items"])

@app.get("/")
def root():
    return {"message": "Welcome to your new Python API!"}

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail="Database connection failed"
        )