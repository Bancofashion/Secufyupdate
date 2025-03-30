from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time, datetime, timedelta
from auth import get_current_user, require_roles

router = APIRouter(
    prefix="/shifts",
    tags=["shifts"]
)

class Shift(BaseModel):
    id: int = 0  # Wordt automatisch ingesteld bij creatie
    employee_ids: List[str] = []  # Meerdere medewerkers kunnen toegewezen worden; leeg betekent open dienst
    shift_date: date
    start_time: time
    end_time: time
    location: str
    status: str = "pending"  # 'pending', 'approved', 'rejected', 'canceled'
    # Extra locatiegegevens:
    titel: Optional[str] = None
    stad: Optional[str] = None
    provincie: Optional[str] = None
    adres: Optional[str] = None
    # Nieuw: vereiste medewerkerprofiel voor deze shift
    required_profile: Optional[str] = None

# In-memory database
fake_shifts_db = []
next_shift_id = 1  # Houdt de volgende beschikbare ID bij

def times_overlap(start1: time, end1: time, start2: time, end2: time) -> bool:
    """
    Controleer of twee tijdsintervallen overlappen.
    We gaan ervan uit dat de shifts op dezelfde dag plaatsvinden.
    """
    return start1 < end2 and start2 < end1

@router.get("/", response_model=List[Shift])
async def get_shifts(current_user: dict = Depends(get_current_user)):
    """Haal alle shifts op. Planners en admins zien alles, medewerkers alleen hun eigen shifts."""
    if current_user["role"] in ["planner", "admin"]:
        return fake_shifts_db
    return [shift for shift in fake_shifts_db if current_user["username"] in shift.get("employee_ids", [])]

@router.get("/{shift_id}", response_model=Shift)
async def get_shift(shift_id: int):
    """Haal een specifieke shift op via het ID."""
    for shift in fake_shifts_db:
        if shift["id"] == shift_id:
            return shift
    raise HTTPException(status_code=404, detail="Shift not found")

@router.post("/", response_model=Shift, status_code=201)
async def create_shift(shift: Shift, current_user: dict = Depends(require_roles(["planner", "planning", "admin"]))):
    """
    Maak een nieuwe shift aan.
    Controleer voor elke medewerker in employee_ids of er geen overlappende shift bestaat op dezelfde dag.
    Als employee_ids leeg is, wordt de shift als open beschouwd.
    """
    global next_shift_id
    for employee in shift.employee_ids:
        for existing in fake_shifts_db:
            if employee in existing.get("employee_ids", []) and existing["shift_date"] == shift.shift_date:
                if times_overlap(shift.start_time, shift.end_time, existing["start_time"], existing["end_time"]):
                    raise HTTPException(status_code=400, detail="Overlapping shift detected for employee {}.".format(employee))
    shift.id = next_shift_id
    next_shift_id += 1
    fake_shifts_db.append(shift.dict())
    return shift

@router.put("/{shift_id}", response_model=Shift)
async def update_shift(shift_id: int, shift: Shift, current_user: dict = Depends(require_roles(["planner", "admin"]))):
    """Werk een bestaande shift bij."""
    for index, existing_shift in enumerate(fake_shifts_db):
        if existing_shift["id"] == shift_id:
            shift.id = shift_id
            fake_shifts_db[index] = shift.dict()
            return shift
    raise HTTPException(status_code=404, detail="Shift not found")

@router.delete("/{shift_id}", response_model=Shift)
async def delete_shift(shift_id: int, current_user: dict = Depends(require_roles(["planner", "admin"]))):
    """Verwijder een shift op basis van het ID."""
    for index, shift in enumerate(fake_shifts_db):
        if shift["id"] == shift_id:
            return fake_shifts_db.pop(index)
    raise HTTPException(status_code=404, detail="Shift not found")

@router.post("/{shift_id}/approve", response_model=Shift)
async def approve_shift(shift_id: int, current_user: dict = Depends(require_roles(["planner", "admin"]))):
    """Keur een shift goed (zet status op 'approved')."""
    for shift in fake_shifts_db:
        if shift["id"] == shift_id:
            shift["status"] = "approved"
            return shift
    raise HTTPException(status_code=404, detail="Shift not found")

@router.post("/{shift_id}/reject", response_model=Shift)
async def reject_shift(shift_id: int, current_user: dict = Depends(require_roles(["planner", "admin"]))):
    """Weiger een shift (zet status op 'rejected')."""
    for shift in fake_shifts_db:
        if shift["id"] == shift_id:
            shift["status"] = "rejected"
            return shift
    raise HTTPException(status_code=404, detail="Shift not found")

@router.post("/{shift_id}/cancel", response_model=Shift)
async def cancel_shift(shift_id: int, current_user: dict = Depends(get_current_user)):
    """
    Annuleer een shift.
    Medewerkers kunnen een shift annuleren als dit minstens 48 uur van tevoren gebeurt.
    Als de annulering binnen 48 uur plaatsvindt, is deze actie alleen toegestaan als de huidige gebruiker een planner of admin is.
    """
    for shift in fake_shifts_db:
        if shift["id"] == shift_id:
            shift_start_datetime = datetime.combine(shift["shift_date"], shift["start_time"])
            now = datetime.utcnow()
            if (shift_start_datetime - now) >= timedelta(hours=48):
                shift["status"] = "canceled"
                return shift
            else:
                if current_user["role"] not in ["planner", "admin"]:
                    raise HTTPException(status_code=403, detail="Cancellation within 48 hours allowed only for planners or admins.")
                shift["status"] = "canceled"
                return shift
    raise HTTPException(status_code=404, detail="Shift not found")

@router.get("/open/diensten", response_model=List[Shift])
async def get_open_diensten(
    stad: Optional[str] = Query(None, description="Filter op stad"),
    provincie: Optional[str] = Query(None, description="Filter op provincie"),
    max_distance: Optional[float] = Query(None, description="Maximum afstand in km"),
    pas_type: Optional[str] = Query(None, description="Filter op vereiste medewerkerprofiel")
):
    """
    Haal alle open diensten (shifts met status 'open' of 'pending') op.
    Optioneel kun je filteren op stad, provincie, maximum afstand (reiskilometers) en pas type.
    """
    open_shifts = [shift for shift in fake_shifts_db if shift.get("status") in ["open", "pending"]]
    if stad:
        open_shifts = [shift for shift in open_shifts if shift.get("stad", "").lower() == stad.lower()]
    if provincie:
        open_shifts = [shift for shift in open_shifts if shift.get("provincie", "").lower() == provincie.lower()]
    if max_distance is not None:
        open_shifts = [shift for shift in open_shifts if shift.get("reiskilometers") is not None and shift.get("reiskilometers") <= max_distance]
    if pas_type:
        open_shifts = [shift for shift in open_shifts if shift.get("required_profile", "").lower() == pas_type.lower()]
    return open_shifts

@router.get("/dienst/{shift_id}", response_model=Shift)
async def dienst_detail(shift_id: int):
    """
    Haal de volledige details van een dienst op, inclusief locatiegegevens (titel, stad, provincie, adres).
    """
    for shift in fake_shifts_db:
        if shift["id"] == shift_id:
            return shift
    raise HTTPException(status_code=404, detail="Dienst niet gevonden")
