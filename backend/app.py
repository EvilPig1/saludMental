from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Permitir el frontend React (cambia el puerto si es diferente)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)

# Modelo para la puntuación
class Score(BaseModel):
    username: str
    score: int

# Modelo para el usuario
class User(BaseModel):
    username: str
    password: str

# Modelo para el usuario en la base de datos
class UserInDB(BaseModel):
    username: str
    hashed_password: str

# Lista de puntuaciones inicial
scores = []

# Lista de usuarios (simulación de base de datos)
fake_users_db = {}

# Configuración de seguridad
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# Ruta de inicio (sirve HTML)
@app.get("/", response_class=HTMLResponse)
async def get_home():
    return """
    <html>
        <head>
            <title>Plataforma de Puntuaciones</title>
        </head>
        <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
            <h1>¡Bienvenido a la Plataforma de Puntuaciones!</h1>
            <p>Este es un servidor API creado con FastAPI.</p>
            <p>Puedes ver las puntuaciones o agregar las tuyas a través de nuestra API.</p>
            <p>Visita la <a href="/scores">ruta de puntuaciones</a> para ver todas las puntuaciones disponibles.</p>
            <p>También puedes hacer una petición POST a <code>/scores</code> para agregar nuevas puntuaciones.</p>
            <p>Explora la <a href="/docs">documentación interactiva de la API aquí</a>.</p>
        </body>
    </html>
    """

# Ruta GET para obtener todas las puntuaciones
@app.get("/scores", response_model=List[Score])
async def get_scores():
    return scores

# Ruta POST para agregar una puntuación
@app.post("/scores", response_model=Score)
async def post_score(score: Score, current_user: User = Depends(get_current_user)):
    new_score = {"username": current_user.username, "score": score.score}
    scores.append(new_score)
    return new_score

# Ruta para registrar un nuevo usuario
@app.post("/register", response_model=User)
async def register_user(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    fake_users_db[user.username] = UserInDB(username=user.username, hashed_password=hashed_password)
    return user

# Ruta para obtener el token de acceso
@app.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Ruta GET para obtener todos los usuarios
@app.get("/users", response_model=List[User])
async def get_users():
    return [User(username=user.username, password=user.hashed_password) for user in fake_users_db.values()]

# Ejecuta con: uvicorn app:app --reload