import secrets
import string
from . import crud
from sqlalchemy.orm import Session

def create_random_key(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return "".join(secrets.choice(chars) for i in range(length))

def create_unique_key(db: Session, length: int = 8) -> str:
    while True:
        key = create_random_key(length)
        db_url = crud.get_db_url_by_key(db, key)
        if not db_url:
            return key
