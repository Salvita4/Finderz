from fastapi import APIRouter, HTTPException, status

from app import bd
from app.schemas import Poi, PoiCreate, PoiUpdate

router = APIRouter(prefix="/pois", tags=["points of interest"])


@router.get("", response_model=list[Poi])
def list_pois():
    return bd.list_values(bd.pois)


@router.get("/{poi_id}", response_model=Poi)
def get_poi(poi_id: str):
    poi = bd.pois.get(poi_id)
    if poi is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de interes no encontrado")
    return poi


@router.post("", response_model=Poi, status_code=status.HTTP_201_CREATED)
def create_poi(payload: PoiCreate):
    if payload.id and payload.id in bd.pois:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un punto con ese id")
    return bd.create_poi(payload)


@router.patch("/{poi_id}", response_model=Poi)
def update_poi(poi_id: str, payload: PoiUpdate):
    poi = bd.pois.get(poi_id)
    if poi is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de interes no encontrado")
    return bd.update_poi(poi, payload)


@router.delete("/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poi(poi_id: str):
    if poi_id not in bd.pois:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de interes no encontrado")
    del bd.pois[poi_id]
