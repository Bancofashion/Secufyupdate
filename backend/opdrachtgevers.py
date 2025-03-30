from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from auth import get_current_user

router = APIRouter(
    prefix="/opdrachtgevers",
    tags=["opdrachtgevers"]
)

class Opdrachtgever(BaseModel):
    id: int = 0  # Wordt automatisch ingesteld bij creatie
    naam: str
    locaties: List[str] = []  # Lijst met locaties van de opdrachtgever

# Simuleer een database met een lijst van opdrachtgevers
fake_opdrachtgevers_db = []
next_opdrachtgever_id = 1

@router.get("/", response_model=List[Opdrachtgever])
async def get_opdrachtgevers(current_user: dict = Depends(get_current_user)):
    """Haal alle opdrachtgevers op. Alleen toegankelijk voor geauthenticeerde gebruikers."""
    return fake_opdrachtgevers_db

@router.get("/{opdrachtgever_id}", response_model=Opdrachtgever)
async def get_opdrachtgever(opdrachtgever_id: int, current_user: dict = Depends(get_current_user)):
    """Haal een specifieke opdrachtgever op via het ID."""
    for opdrachtgever in fake_opdrachtgevers_db:
        if opdrachtgever["id"] == opdrachtgever_id:
            return opdrachtgever
    raise HTTPException(status_code=404, detail="Opdrachtgever not found")

@router.post("/", response_model=Opdrachtgever, status_code=201)
async def create_opdrachtgever(opdrachtgever: Opdrachtgever, current_user: dict = Depends(get_current_user)):
    """Maak een nieuwe opdrachtgever aan."""
    global next_opdrachtgever_id
    opdrachtgever_dict = opdrachtgever.dict()
    opdrachtgever_dict["id"] = next_opdrachtgever_id
    next_opdrachtgever_id += 1
    fake_opdrachtgevers_db.append(opdrachtgever_dict)
    return opdrachtgever_dict

@router.put("/{opdrachtgever_id}", response_model=Opdrachtgever)
async def update_opdrachtgever(opdrachtgever_id: int, opdrachtgever: Opdrachtgever, current_user: dict = Depends(get_current_user)):
    """Werk een bestaande opdrachtgever bij."""
    for index, existing_opdrachtgever in enumerate(fake_opdrachtgevers_db):
        if existing_opdrachtgever["id"] == opdrachtgever_id:
            updated_opdrachtgever = opdrachtgever.dict()
            updated_opdrachtgever["id"] = opdrachtgever_id
            fake_opdrachtgevers_db[index] = updated_opdrachtgever
            return updated_opdrachtgever
    raise HTTPException(status_code=404, detail="Opdrachtgever not found")

@router.delete("/{opdrachtgever_id}", response_model=Opdrachtgever)
async def delete_opdrachtgever(opdrachtgever_id: int, current_user: dict = Depends(get_current_user)):
    """Verwijder een opdrachtgever op basis van ID."""
    for index, opdrachtgever in enumerate(fake_opdrachtgevers_db):
        if opdrachtgever["id"] == opdrachtgever_id:
            removed_opdrachtgever = fake_opdrachtgevers_db.pop(index)
            return removed_opdrachtgever
    raise HTTPException(status_code=404, detail="Opdrachtgever not found")
