from datetime import datetime, timedelta
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext  # Voor veilige wachtwoordhashing

# Configuratie voor JWT
SECRET_KEY = "mijnzeergeheime_sleutel"  # Gebruik in productie een veilige, omgevingsvariabele
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Wachtwoord hashing configuratie
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic-modellen
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    role: str
    email: Optional[str] = None

class RolePermissions(BaseModel):
    permissions: List[str]

# Dummy gebruikersdatabase met gehashte wachtwoorden
fake_users_db = {
    "planner1": {
        "username": "planner1",
        "full_name": "Planner One",
        "email": "planner1@example.com",
        "hashed_password": pwd_context.hash("planner123"),
        "role": "planner"
    },
    "medewerker1": {
        "username": "medewerker1",
        "full_name": "Medewerker One",
        "email": "medewerker1@example.com",
        "hashed_password": pwd_context.hash("medewerker123"),
        "role": "medewerker"
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin"
    }
}

# Dummy rollenbeheer
roles_permissions: Dict[str, List[str]] = {
    "admin": ["manage_users", "manage_roles", "manage_shifts", "manage_invoices"],
    "planner": ["manage_shifts"],
    "boekhouding": ["manage_invoices"],
    "medewerker": ["view_own_data"]
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> Optional[dict]:
    return fake_users_db.get(username)

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return User(username=user["username"], role=user["role"], email=user.get("email"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Login endpoint dat form-data accepteert (standaard)
@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldige gebruikersnaam of wachtwoord",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Nieuw: JSON-login endpoint (optioneel, als je JSON wilt gebruiken)
@router.post("/token_json", response_model=Token)
async def login_json(token_request: TokenRequest):
    user = authenticate_user(token_request.username, token_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldige gebruikersnaam of wachtwoord",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Ongeldige authenticatiegegevens")
        # Haal aanvullende gegevens op, bv. email
        user_data = get_user(username)
        email = user_data.get("email") if user_data else None
        return {"username": username, "role": role, "email": email}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldige authenticatiegegevens",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_roles(required_roles: List[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Onvoldoende rechten")
        return current_user
    return role_checker

# Endpoint voor het ophalen van de huidige gebruiker
@router.get("/users/me/profile", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return User(username=current_user["username"], role=current_user["role"], email=current_user.get("email"))

# Rolbeheer endpoints
@router.post("/roles", response_model=dict)
async def create_role(role_name: str, permissions: List[str], current_user: dict = Depends(require_roles(["admin"]))):
    if role_name in roles_permissions:
        raise HTTPException(status_code=400, detail="Rol bestaat al.")
    roles_permissions[role_name] = permissions
    return {"message": f"Rol '{role_name}' aangemaakt."}

@router.put("/roles/{role_name}", response_model=dict)
async def update_role(role_name: str, permissions: List[str], current_user: dict = Depends(require_roles(["admin"]))):
    if role_name not in roles_permissions:
        raise HTTPException(status_code=404, detail="Rol niet gevonden.")
    roles_permissions[role_name] = permissions
    return {"message": f"Rol '{role_name}' bijgewerkt."}

@router.delete("/roles/{role_name}", response_model=dict)
async def delete_role(role_name: str, current_user: dict = Depends(require_roles(["admin"]))):
    if role_name == "admin":
        raise HTTPException(status_code=403, detail="De admin rol kan niet worden verwijderd.")
    if role_name not in roles_permissions:
        raise HTTPException(status_code=404, detail="Rol niet gevonden.")
    del roles_permissions[role_name]
    return {"message": f"Rol '{role_name}' verwijderd."}

@router.get("/roles", response_model=dict)
async def list_roles(current_user: dict = Depends(require_roles(["admin"]))):
    return roles_permissions
