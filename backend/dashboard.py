from fastapi import APIRouter, Depends
from auth import require_roles
from planning import fake_shifts_db
from dienstaanvragen import fake_dienstaanvragen_db
from facturatie import fake_facturen_db
from datetime import datetime
from scheduler import calculate_shift_hours

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/")
async def get_dashboard(current_user: dict = Depends(require_roles(["planner", "admin"]))):
    shift_stats = {}
    total_shift_hours = 0.0
    for shift in fake_shifts_db:
        status = shift.get("status", "unknown")
        shift_stats[status] = shift_stats.get(status, 0) + 1
        try:
            day_hours, evening_hours, night_hours = calculate_shift_hours(shift["start_time"], shift["end_time"])
            total_shift_hours += (day_hours + evening_hours + night_hours)
        except Exception as e:
            print("Fout bij urenberekening voor shift {}: {}".format(shift.get("id"), e))
            continue

    aanvraag_stats = {}
    for aanvraag in fake_dienstaanvragen_db:
        status = aanvraag.get("status", "unknown")
        aanvraag_stats[status] = aanvraag_stats.get(status, 0) + 1

    factuur_stats = {}
    total_factuur_amount = 0.0
    for factuur in fake_facturen_db:
        status = factuur.get("status", "unknown")
        factuur_stats[status] = factuur_stats.get(status, 0) + 1
        try:
            total_factuur_amount += float(factuur.get("bedrag", 0))
        except Exception as e:
            print("Fout bij factuur bedrag voor factuur {}: {}".format(factuur.get("id"), e))
            continue

    dashboard_data = {
        "total_shifts": len(fake_shifts_db),
        "shift_stats": shift_stats,
        "total_shift_hours": total_shift_hours,
        "total_dienstaanvragen": len(fake_dienstaanvragen_db),
        "dienstaanvraag_stats": aanvraag_stats,
        "total_facturen": len(fake_facturen_db),
        "factuur_stats": factuur_stats,
        "total_factuur_amount": total_factuur_amount,
        "timestamp": datetime.now().isoformat()
    }
    return dashboard_data
