from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from planning import router as planning_router
from facturatie import router as facturatie_router
from opdrachtgevers import router as opdrachtgevers_router
from export import router as export_router
from tijdlijn import router as tijdlijn_router
from favorieten import router as favorieten_router
from agenda import router as agenda_router
from auto_approval import router as auto_approval_router
from dienstaanvragen import router as dienstaanvragen_router
from factuursjablonen import router as factuursjablonen_router
from dashboard import router as dashboard_router
from tarieven import router as tarieven_router
from pdf_export import router as pdf_export_router
from verloning import router as verloning_router

app = FastAPI(
    title="Medewerker Planning en Facturatie Systeem",
    description="API voor het beheren van planning, facturatie en verloning.",
    version="0.1.0"
)

# ✅ CORS-instellingen toevoegen om frontend toegang te geven tot de API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Zet hier specifieke domeinen als je het wilt beperken (bv. ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],  # Staat GET, POST, PUT, DELETE etc. toe
    allow_headers=["*"],  # Staat alle headers toe, inclusief Authorization (voor tokens)
)

@app.get("/")
async def root():
    return {"message": "Welkom bij het Planning en Facturatie Systeem!"}

# ✅ Alle API-routers opnemen
app.include_router(users_router)
app.include_router(planning_router)
app.include_router(facturatie_router)
app.include_router(verloning_router)
app.include_router(auth_router)
app.include_router(opdrachtgevers_router)
app.include_router(export_router)
app.include_router(tijdlijn_router)
app.include_router(favorieten_router)
app.include_router(agenda_router)
app.include_router(auto_approval_router)
app.include_router(dienstaanvragen_router)
app.include_router(factuursjablonen_router)
app.include_router(dashboard_router)
app.include_router(tarieven_router)
app.include_router(pdf_export_router)

# ✅ Start de server correct
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
