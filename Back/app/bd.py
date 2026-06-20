from itertools import count
from typing import TypeVar

from app.schemas import (
    Friend,
    FriendCreate,
    FriendUpdate,
    PanicAlert,
    PanicAlertCreate,
    Poi,
    PoiCreate,
    PoiUpdate,
    Promotion,
    PromotionCreate,
    PromotionUpdate,
)

T = TypeVar("T")

_friend_ids = count(6)
_poi_ids = count(1)
_promotion_ids = count(5)
_panic_ids = count(1)

friends: dict[str, Friend] = {
    "1": Friend(id="1", name="Ana", x=62, y=38, status="online", faro=True, battery=84, group="crew"),
    "2": Friend(id="2", name="Carlos", x=30, y=55, status="online", faro=True, battery=61, group="crew"),
    "3": Friend(id="3", name="Maria", x=78, y=62, status="online", faro=False, battery=23, group="crew"),
    "4": Friend(id="4", name="Juan", x=22, y=42, status="offline", faro=False, battery=0, group="col"),
    "5": Friend(id="5", name="Sofia", x=52, y=72, status="online", faro=False, battery=55, group="col"),
}

pois: dict[str, Poi] = {
    "mainStage": Poi(id="mainStage", name="Main Stage", type="stage", wx=0, wz=-12, icon="🎤"),
    "stage2": Poi(id="stage2", name="Stage 2", type="stage", wx=11.5, wz=-7, icon="🎸"),
    "techDome": Poi(id="techDome", name="Techno Dome", type="stage", wx=-11.5, wz=-7, icon="🎧"),
    "vip": Poi(id="vip", name="VIP Zone", type="vip", wx=7, wz=-3, icon="⭐"),
    "foodCourt": Poi(id="foodCourt", name="Food Court", type="food", wx=9.5, wz=9.5, icon="🍔"),
    "beerGarden": Poi(id="beerGarden", name="Beer Garden", type="bar", wx=-5.5, wz=2, icon="🍺"),
    "camping": Poi(id="camping", name="Camping", type="food", wx=-9.5, wz=9.5, icon="⛺"),
    "medical": Poi(id="medical", name="Medico", type="medical", wx=-3.5, wz=5.8, icon="🏥"),
    "info": Poi(id="info", name="Info / Merch", type="info", wx=3.5, wz=4, icon="ℹ️"),
    "restroomW": Poi(id="restroomW", name="Banos Oeste", type="restroom", wx=-13.5, wz=2, icon="🚻"),
    "restroomE": Poi(id="restroomE", name="Banos Este", type="restroom", wx=13.5, wz=2, icon="🚻"),
    "exitN": Poi(id="exitN", name="Salida Norte", type="exit", wx=0, wz=-16, icon="🚪"),
    "exitS": Poi(id="exitS", name="Salida Sur", type="exit", wx=0, wz=16, icon="🚪"),
}

promotions: dict[str, Promotion] = {
    "p1": Promotion(
        id="p1",
        title="2x1 en Corona",
        description="Dos cervezas al precio de una en barra principal.",
        discount="2x1",
        stallName="Beer Garden",
        stallId="beerGarden",
        wx=-5.5,
        wz=2,
        expiresIn=18,
        color="#f59e0b",
        icon="🍺",
        category="drink",
        used=False,
    ),
    "p2": Promotion(
        id="p2",
        title="Combo Burger + Papas",
        description="Hamburguesa completa con papas por precio especial.",
        discount="-30%",
        stallName="Food Court",
        stallId="foodCourt",
        wx=9.5,
        wz=9.5,
        expiresIn=35,
        color="#ef4444",
        icon="🍔",
        category="food",
        used=False,
    ),
    "p3": Promotion(
        id="p3",
        title="Merch Oficial Exclusivo",
        description="Remeras y gorras del festival con 25% off.",
        discount="-25%",
        stallName="Info / Merch",
        stallId="info",
        wx=3.5,
        wz=4,
        expiresIn=60,
        color="#8b5cf6",
        icon="👕",
        category="merch",
        used=False,
    ),
    "p4": Promotion(
        id="p4",
        title="Shot de Tequila Gratis",
        description="Un shot gratis con cualquier compra en VIP Bar.",
        discount="FREE",
        stallName="VIP Zone",
        stallId="vip",
        wx=7,
        wz=-3,
        expiresIn=8,
        color="#06b6d4",
        icon="🥃",
        category="drink",
        used=False,
    ),
}

panic_alerts: dict[str, PanicAlert] = {}


def list_values(storage: dict[str, T]) -> list[T]:
    return list(storage.values())


def create_friend(payload: FriendCreate) -> Friend:
    friend_id = payload.id or str(next(_friend_ids))
    friend = Friend(id=friend_id, **payload.model_dump(exclude={"id"}))
    friends[friend_id] = friend
    return friend


def update_friend(friend: Friend, payload: FriendUpdate) -> Friend:
    updated = friend.model_copy(update=payload.model_dump(exclude_unset=True))
    friends[updated.id] = updated
    return updated


def create_poi(payload: PoiCreate) -> Poi:
    poi_id = payload.id or f"poi{next(_poi_ids)}"
    poi = Poi(id=poi_id, **payload.model_dump(exclude={"id"}))
    pois[poi_id] = poi
    return poi


def update_poi(poi: Poi, payload: PoiUpdate) -> Poi:
    updated = poi.model_copy(update=payload.model_dump(exclude_unset=True))
    pois[updated.id] = updated
    return updated


def create_promotion(payload: PromotionCreate) -> Promotion:
    promotion_id = payload.id or f"p{next(_promotion_ids)}"
    promotion = Promotion(id=promotion_id, **payload.model_dump(exclude={"id"}))
    promotions[promotion_id] = promotion
    return promotion


def update_promotion(promotion: Promotion, payload: PromotionUpdate) -> Promotion:
    updated = promotion.model_copy(update=payload.model_dump(exclude_unset=True))
    promotions[updated.id] = updated
    return updated


def create_panic_alert(payload: PanicAlertCreate) -> PanicAlert:
    alert_id = f"panic{next(_panic_ids)}"
    alert = PanicAlert(id=alert_id, **payload.model_dump())
    panic_alerts[alert_id] = alert
    return alert
