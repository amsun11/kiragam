from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import config
from pipeline import get_route
#Claude came upw with the two classes Coordinate and RouteRequest to help with the structure of this file
app = FastAPI()

allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?", # include any local server

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kiragam-frontend.onrender.com",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class Coordinate(BaseModel):
    lon: float
    lat: float

class RouteRequest(BaseModel):
    region_id:str
    start: Coordinate
    end: Coordinate
    max_slope_deg: float = config.SAFE_SLOPE_LIMIT

@app.post("/api/route")
def calculate_route(data: RouteRequest):
    print("START:", data.start.lat, data.start.lon, flush=True)
    print("END:", data.end.lat, data.end.lon, flush=True)

    if data.region_id != "gale":
        raise HTTPException(
            status_code=400,
            detail="Unsupported region"
        )

    try:
        result = get_route(
            data.start.lat,
            data.start.lon,
            data.end.lat,
            data.end.lon
        )

        return {
            "path": [
                {
                    "lon": point["longitude"],
                    "lat": point["latitude"]
                }
                for point in result["path"]
            ],
            "stats": result["stats"],
            "meta": {
                "mock": False
            }
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
