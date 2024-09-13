# auth.py
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import os
import bcrypt

# Configurações do JWT
SECRET_KEY = "mysecretkey"  # Mantenha essa chave segura em produção
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configura o contexto para criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos
class User(BaseModel):
    username: str
    password: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funções para hashing e verificação de senhas
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Função para criar o token de acesso
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(username: str) -> Optional[UserInDB]:
    users_db = read_users_from_file("credentials.txt")
    hashed_password = users_db.get(username)
    if hashed_password:
        return UserInDB(username=username, hashed_password=hashed_password)
    return None

# Função para obter o usuário atual a partir do token
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="credenciais invalidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
def read_users_from_file(file_path: str) -> Dict[str, str]:
    """Lê os usuários e senhas hasheadas do arquivo e retorna um dicionário."""
    users_db = {}
    
    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        return users_db
    
    try:
        # Abre o arquivo e lê as linhas
        with open(file_path, "r") as file:
            for line in file:
                username, hashed_password = line.strip().split(":", 1)
                users_db[username] = hashed_password
    except Exception as e:
        print(f"Erro ao ler o arquivo de credenciais: {e}")
    
    return users_db
