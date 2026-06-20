from fastapi import APIRouter, HTTPException, status

from app import bd
from app.schemas import Friend, FriendCreate, FriendUpdate

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("", response_model=list[Friend])
def list_friends():
    return bd.list_values(bd.friends)


@router.get("/{friend_id}", response_model=Friend)
def get_friend(friend_id: str):
    friend = bd.friends.get(friend_id)
    if friend is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amigo no encontrado")
    return friend


@router.post("", response_model=Friend, status_code=status.HTTP_201_CREATED)
def create_friend(payload: FriendCreate):
    if payload.id and payload.id in bd.friends:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un amigo con ese id")
    return bd.create_friend(payload)


@router.patch("/{friend_id}", response_model=Friend)
def update_friend(friend_id: str, payload: FriendUpdate):
    friend = bd.friends.get(friend_id)
    if friend is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amigo no encontrado")
    return bd.update_friend(friend, payload)


@router.patch("/{friend_id}/faro", response_model=Friend)
def toggle_faro(friend_id: str):
    friend = bd.friends.get(friend_id)
    if friend is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amigo no encontrado")
    return bd.update_friend(friend, FriendUpdate(faro=not friend.faro))


@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_friend(friend_id: str):
    if friend_id not in bd.friends:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amigo no encontrado")
    del bd.friends[friend_id]
