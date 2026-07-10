from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from schemas import VisitCreate
from geo_utils import reverse_geocode

app = FastAPI()

# Allow all origins so Swagger UI, QR scan from any device, and Render work correctly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

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




@app.post("/api/visit")
def log_visit(visit: VisitCreate, db: Session = Depends(get_db)):
    try:
        print("Received:", visit)

        place, suburb, road, pincode = None, None, None, None

        if visit.permission_granted and visit.latitude is not None:
            place, suburb, road, pincode = reverse_geocode(
                visit.latitude,
                visit.longitude
            )

        new_visit = models.Visit(
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

        print("Inserted ID:", new_visit.id)

        return {
            "status": "success",
            "visit_id": new_visit.id
        }

    except Exception as e:
        print("ERROR:", repr(e))
        raise