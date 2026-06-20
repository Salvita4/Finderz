from fastapi import APIRouter, HTTPException, status

from app import bd
from app.schemas import PanicAlert, PanicAlertCreate

router = APIRouter(prefix="/panic-alerts", tags=["panic alerts"])


@router.get("", response_model=list[PanicAlert])
def list_panic_alerts(active_only: bool = False):
    alerts = bd.list_values(bd.panic_alerts)
    if active_only:
        return [alert for alert in alerts if alert.active]
    return alerts


@router.post("", response_model=PanicAlert, status_code=status.HTTP_201_CREATED)
def create_panic_alert(payload: PanicAlertCreate):
    if payload.friendId not in bd.friends:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amigo no encontrado")
    return bd.create_panic_alert(payload)


@router.patch("/{alert_id}/resolve", response_model=PanicAlert)
def resolve_panic_alert(alert_id: str):
    alert = bd.panic_alerts.get(alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")
    resolved = alert.model_copy(update={"active": False})
    bd.panic_alerts[alert_id] = resolved
    return resolved
