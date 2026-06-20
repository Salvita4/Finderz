from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class FriendStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"


class PoiType(StrEnum):
    STAGE = "stage"
    FOOD = "food"
    BAR = "bar"
    RESTROOM = "restroom"
    INFO = "info"
    MEDICAL = "medical"
    EXIT = "exit"
    VIP = "vip"


class PromotionCategory(StrEnum):
    DRINK = "drink"
    FOOD = "food"
    MERCH = "merch"
    EXPERIENCE = "experience"


class FriendBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)
    status: FriendStatus = FriendStatus.ONLINE
    faro: bool = False
    battery: int = Field(ge=0, le=100)
    group: Optional[str] = Field(default=None, max_length=50)


class FriendCreate(FriendBase):
    id: Optional[str] = None


class FriendUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    x: Optional[float] = Field(default=None, ge=0, le=100)
    y: Optional[float] = Field(default=None, ge=0, le=100)
    status: Optional[FriendStatus] = None
    faro: Optional[bool] = None
    battery: Optional[int] = Field(default=None, ge=0, le=100)
    group: Optional[str] = Field(default=None, max_length=50)


class Friend(FriendBase):
    id: str


class PoiBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: PoiType
    wx: float
    wz: float
    icon: str = Field(min_length=1, max_length=8)


class PoiCreate(PoiBase):
    id: Optional[str] = None


class PoiUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    type: Optional[PoiType] = None
    wx: Optional[float] = None
    wz: Optional[float] = None
    icon: Optional[str] = Field(default=None, min_length=1, max_length=8)


class Poi(PoiBase):
    id: str


class PromotionBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=300)
    discount: str = Field(min_length=1, max_length=30)
    stallName: str = Field(min_length=1, max_length=100)
    stallId: str = Field(min_length=1, max_length=80)
    wx: float
    wz: float
    expiresIn: int = Field(ge=0)
    color: str = Field(min_length=4, max_length=30)
    icon: str = Field(min_length=1, max_length=8)
    category: PromotionCategory
    used: bool = False
    isNew: bool = False


class PromotionCreate(PromotionBase):
    id: Optional[str] = None


class PromotionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, min_length=1, max_length=300)
    discount: Optional[str] = Field(default=None, min_length=1, max_length=30)
    stallName: Optional[str] = Field(default=None, min_length=1, max_length=100)
    stallId: Optional[str] = Field(default=None, min_length=1, max_length=80)
    wx: Optional[float] = None
    wz: Optional[float] = None
    expiresIn: Optional[int] = Field(default=None, ge=0)
    color: Optional[str] = Field(default=None, min_length=4, max_length=30)
    icon: Optional[str] = Field(default=None, min_length=1, max_length=8)
    category: Optional[PromotionCategory] = None
    used: Optional[bool] = None
    isNew: Optional[bool] = None


class Promotion(PromotionBase):
    id: str


class PanicAlertCreate(BaseModel):
    friendId: str = Field(min_length=1)
    message: str = Field(default="Necesito ayuda", min_length=1, max_length=200)
    wx: float
    wz: float


class PanicAlert(PanicAlertCreate):
    id: str
    active: bool = True
