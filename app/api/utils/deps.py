from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        raise e
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]
