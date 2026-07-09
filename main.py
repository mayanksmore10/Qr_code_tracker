from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from schemas import VisitCreate
from geo_utils import reverse_geocode

app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def qr_webpage():
    return FileResponse("templates/index.html")


@app.get("/success")
def success_page():
    return FileResponse("templates/success.html")


@app.get("/permission-denied")
def permission_denied_page():
    return FileResponse("templates/permission_denied.html")


# This is the route your QR code should actually point to.
# It serves the same index.html but passes qr_id in so the JS knows
# which QR was scanned.
@app.get("/track/{qr_id}")
def track_visitor(qr_id: str, request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "qr_id": qr_id
    })


@app.post("/api/log-visit")
def log_visit(visit: VisitCreate, db: Session = Depends(get_db)):
    place, suburb, road, pincode = None, None, None, None

    # Only attempt reverse geocoding if permission was granted AND
    # coordinates actually exist - skips it entirely on denial, no crash risk.
    if visit.permission_granted and visit.latitude is not None and visit.longitude is not None:
        place, suburb, road, pincode = reverse_geocode(visit.latitude, visit.longitude)

    new_visit = models.Visit(
        qr_id=visit.qr_id,
        latitude=visit.latitude,
        longitude=visit.longitude,
        place=place,
        suburb=suburb,
        road=road,
        pincode=pincode,
        permission_granted=visit.permission_granted
    )

    db.add(new_visit)
    db.commit()
    db.refresh(new_visit)

    if visit.permission_granted:
        message = "Permission granted. Ok."
    else:
        message = "Please grant location permission to proceed."

    return {
        "status": "success",
        "message": message,
        "visit_id": new_visit.id
    }