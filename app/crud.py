from . import models, key_gen
from sqlalchemy.orm import Session

def get_db_url_by_key(db: Session, url_key: str):
    return db.query(models.URL).filter(models.URL.key == url_key).first()

def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
    return db.query(models.URL).filter(models.URL.secret_key == secret_key).first()


def create_db_url(db: Session, url_key: str, secret_key: str, target_url: str):
    key = key_gen.create_unique_key(db)
    secret_key = f"{key}_{key_gen.create_random_key(length=8)}"
    db_url = models.URL(key=url_key, secret_key=secret_key, target_url=target_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def update_clicks(db: Session, db_url: models.URL):
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url

def delete_url(db: Session, secret_key: str):
    db_url = get_db_url_by_secret_key(db, secret_key)
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url