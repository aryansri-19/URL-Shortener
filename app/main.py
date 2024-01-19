from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import validators
import secrets
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from .database import SessionLocal, engine
from . import schemas, models, key_gen, crud
from .config import get_settings

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def raise_bad_message(message):
    raise HTTPException(status_code=400, detail=message)

def raise_not_found(request):
    raise HTTPException(status_code=404, detail=f"URL not found for {request.url}")

def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for("admin", secret_key=db_url.secret_key)
    db_url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url

@app.get("/{url_key}")
def forward_url(url_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := crud.get_db_url_by_key(db, url_key):
        crud.update_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)

@app.post("/url", response_model=schemas.URLInfo)
def shorten(url: schemas.URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_message("Invalid URL")

    db_url = crud.get_db_url_by_key(db, url)
    return get_admin_info(db_url)

@app.get("/admin/{secret_key}", name="admin", response_model=schemas.URLInfo)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)

@app.delete("/admin/{secret_key}")
def delete_url(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := crud.delete_url(db, secret_key):
        return {"message": f"URL {db_url.key} deleted"}
    else:
        raise_not_found(request)

@app.get("/")
def home():
    return {"message": "Shorten URL API"}