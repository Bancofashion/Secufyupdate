from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime, date
from auth import get_current_user, require_roles
from planning import fake_shifts_db  # Shift data
from email_utils import send_shift_registration_email, send_shift_unregistration_email

router = APIRouter(
    prefix="/dienstaanvragen",
    tags=["dienstaanvragen"]
)


class DienstAanvraag(BaseModel):
    id: int = 0  # Wordt automatisch ingesteld bij creatie
    shift_id: int  # De ID van de shift waarop wordt gereageerd
    employee_id: str = ""  # Wordt automatisch ingesteld op basis van de ingelogde gebruiker
    aanvraag_date: date = None
    status: str = "requested"  # Mogelijke waarden: "requested", "approved", "rejected"


fake_dienstaanvragen_db: List[dict] = []
next_aanvraag_id = 1


@router.get("/", response_model=List[DienstAanvraag])
async def get_dienstaanvragen(current_user: dict = Depends(get_current_user)):
    """
    Haal dienstaanvragen op.
    - Medewerkers zien alleen hun eigen aanvragen.
    - Planners en admins zien alle aanvragen.
    """
    if current_user["role"] in ["planner", "admin"]:
        return fake_dienstaanvragen_db
    return [aanvraag for aanvraag in fake_dienstaanvragen_db if aanvraag["employee_id"] == current_user["username"]]


@router.post("/", response_model=DienstAanvraag, status_code=201)
async def create_dienstaanvraag(aanvraag: DienstAanvraag, current_user: dict = Depends(get_current_user)):
    """
    Medewerkers dienen een dienstaanvraag in voor een specifieke shift.
    Het veld employee_id wordt overschreven met de ingelogde gebruiker en de aanvraag_date wordt op vandaag gezet.
    Na succesvolle indiening wordt er een e-mail gestuurd naar de medewerker ter bevestiging van de inschrijving.
    """
    global next_aanvraag_id
    aanvraag_dict = aanvraag.dict()
    aanvraag_dict["employee_id"] = current_user["username"]
    aanvraag_dict["aanvraag_date"] = datetime.utcnow().date()
    aanvraag_dict["id"] = next_aanvraag_id
    next_aanvraag_id += 1
    fake_dienstaanvragen_db.append(aanvraag_dict)

    # Haal de shiftdetails op uit fake_shifts_db op basis van de shift_id
    shift = next((s for s in fake_shifts_db if s["id"] == aanvraag.shift_id), None)
    if shift:
        # Veronderstel dat current_user een 'email' veld heeft; zo niet, gebruik een standaardwaarde
        employee_email = current_user.get("email", "default@example.com")
        send_shift_registration_email(employee_email, shift)

    return aanvraag_dict


@router.post("/{aanvraag_id}/approve", response_model=DienstAanvraag)
async def approve_dienstaanvraag(aanvraag_id: int, current_user: dict = Depends(require_roles(["planner", "admin"]))):
    """
    Planners of admins kunnen een dienstaanvraag goedkeuren.
    """
    for aanvraag in fake_dienstaanvragen_db:
        if aanvraag["id"] == aanvraag_id:
            aanvraag["status"] = "approved"
            return aanvraag
    raise HTTPException(status_code=404, detail="Dienstaanvraag niet gevonden")


@router.post("/{aanvraag_id}/reject", response_model=DienstAanvraag)
async def reject_dienstaanvraag(aanvraag_id: int, current_user: dict = Depends(require_roles(["planner", "admin"]))):
    """
    Planners of admins kunnen een dienstaanvraag afwijzen.
    """
    for aanvraag in fake_dienstaanvragen_db:
        if aanvraag["id"] == aanvraag_id:
            aanvraag["status"] = "rejected"
            return aanvraag
    raise HTTPException(status_code=404, detail="Dienstaanvraag niet gevonden")


@router.delete("/{aanvraag_id}", response_model=DienstAanvraag)
async def delete_dienstaanvraag(aanvraag_id: int, current_user: dict = Depends(get_current_user)):
    """
    Een medewerker kan zijn eigen dienstaanvraag intrekken, mits deze nog in de status 'requested' is.
    Planners of admins kunnen elke aanvraag verwijderen.
    Na uitschrijving wordt er een e-mail verstuurd naar de medewerker.
    """
    for idx, aanvraag in enumerate(fake_dienstaanvragen_db):
        if aanvraag["id"] == aanvraag_id:
            if current_user["role"] not in ["planner", "admin"]:
                if aanvraag["employee_id"] != current_user["username"] or aanvraag["status"] != "requested":
                    raise HTTPException(status_code=403, detail="Je kunt deze aanvraag niet verwijderen.")

            # Haal de shiftdetails op voordat de aanvraag wordt verwijderd
            shift = next((s for s in fake_shifts_db if s["id"] == aanvraag["shift_id"]), None)
            removed = fake_dienstaanvragen_db.pop(idx)

            if shift:
                employee_email = current_user.get("email", "default@example.com")
                send_shift_unregistration_email(employee_email, shift)

            return removed
    raise HTTPException(status_code=404, detail="Dienstaanvraag niet gevonden")
