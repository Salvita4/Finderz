from fastapi import APIRouter, HTTPException, status

from app import bd
from app.schemas import Promotion, PromotionCreate, PromotionUpdate

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.get("", response_model=list[Promotion])
def list_promotions(include_used: bool = True):
    promotions = bd.list_values(bd.promotions)
    if include_used:
        return promotions
    return [promotion for promotion in promotions if not promotion.used]


@router.get("/{promotion_id}", response_model=Promotion)
def get_promotion(promotion_id: str):
    promotion = bd.promotions.get(promotion_id)
    if promotion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocion no encontrada")
    return promotion


@router.post("", response_model=Promotion, status_code=status.HTTP_201_CREATED)
def create_promotion(payload: PromotionCreate):
    if payload.id and payload.id in bd.promotions:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una promocion con ese id")
    return bd.create_promotion(payload)


@router.patch("/{promotion_id}", response_model=Promotion)
def update_promotion(promotion_id: str, payload: PromotionUpdate):
    promotion = bd.promotions.get(promotion_id)
    if promotion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocion no encontrada")
    return bd.update_promotion(promotion, payload)


@router.patch("/{promotion_id}/use", response_model=Promotion)
def use_promotion(promotion_id: str):
    promotion = bd.promotions.get(promotion_id)
    if promotion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocion no encontrada")
    return bd.update_promotion(promotion, PromotionUpdate(used=True, isNew=False))


@router.patch("/{promotion_id}/clear-new", response_model=Promotion)
def clear_new_promotion(promotion_id: str):
    promotion = bd.promotions.get(promotion_id)
    if promotion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocion no encontrada")
    return bd.update_promotion(promotion, PromotionUpdate(isNew=False))


@router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promotion(promotion_id: str):
    if promotion_id not in bd.promotions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocion no encontrada")
    del bd.promotions[promotion_id]
