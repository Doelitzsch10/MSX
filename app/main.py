from typing import List
from fastapi import FastAPI, Depends, HTTPException
from app.models import Veiculo, VeiculoInDB, StatusUpdate
from app.auth import create_access_token, get_current_user, User, Token, TokenData
from app.auth import verify_password, get_password_hash, get_user, read_users_from_file

app = FastAPI()

# Simulação de banco de dados
class VeiculoDB:
    def __init__(self):
        self.veiculos = []
        self.next_id = 1
        self.initialize()

    def initialize(self):
        self.veiculos = [
            VeiculoInDB(id=self.next_id, nome="Fusca", modelo="Volkswagen Fusca", status="CONECTADO"),
            VeiculoInDB(id=self.next_id + 1, nome="Civic", modelo="Honda Civic", status="DESCONECTADO"),
            VeiculoInDB(id=self.next_id + 2, nome="Corsa", modelo="Chevrolet Corsa", status="CONECTADO"),
            VeiculoInDB(id=self.next_id + 3, nome="Onix", modelo="Chevrolet Onix", status="DESCONECTADO"),
            VeiculoInDB(id=self.next_id + 4, nome="Focus", modelo="Ford Focus", status="CONECTADO"),
            VeiculoInDB(id=self.next_id + 5, nome="Golf", modelo="Volkswagen Golf", status="DESCONECTADO"),
        ]
        self.next_id += len(self.veiculos)

    def add_veiculo(self, veiculo: Veiculo) -> VeiculoInDB:
        veiculo_db = VeiculoInDB(id=self.next_id, **veiculo.model_dump())
        self.next_id += 1
        self.veiculos.append(veiculo_db)
        return veiculo_db

    def get_veiculo_by_nome(self, nome: str) -> VeiculoInDB:
        veiculo = next((v for v in self.veiculos if v.nome == nome), None)
        if veiculo is None:
            raise HTTPException(status_code=404, detail="Veículo não encontrado")
        return veiculo

    def update_veiculo(self, nome: str, status: str) -> VeiculoInDB:
        veiculo = self.get_veiculo_by_nome(nome)
        if status not in ["CONECTADO", "DESCONECTADO"]:
            raise HTTPException(status_code=400, detail="Status inválido")
        veiculo.status = status
        return veiculo

    def delete_veiculo(self, nome: str) -> VeiculoInDB:
        veiculo = self.get_veiculo_by_nome(nome)
        self.veiculos = [v for v in self.veiculos if v.nome != nome]
        return veiculo

veiculo_db = VeiculoDB()

@app.post("/token", response_model=Token)
async def login(user: User):
    credentials_db = read_users_from_file("credentials.txt")
    hashed_password = credentials_db.get(user.username)
    if not hashed_password or not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/veiculos", response_model=List[str])
async def listar_nomes_veiculos(current_user: TokenData = Depends(get_current_user)):
    return [veiculo.nome for veiculo in veiculo_db.veiculos]

@app.post("/veiculos", response_model=Veiculo)
async def criar_veiculo(veiculo: Veiculo, current_user: TokenData = Depends(get_current_user)):
    return veiculo_db.add_veiculo(veiculo)

@app.get("/veiculos/{nome_veiculo}", response_model=VeiculoInDB)
async def obter_veiculo_por_nome(nome_veiculo: str, current_user: TokenData = Depends(get_current_user)):
    return veiculo_db.get_veiculo_by_nome(nome_veiculo)

@app.put("/veiculos/{nome_veiculo}", response_model=VeiculoInDB)
async def atualizar_veiculo(nome_veiculo: str, status_update: StatusUpdate, current_user: TokenData = Depends(get_current_user)):
    return veiculo_db.update_veiculo(nome_veiculo, status_update.status)

@app.delete("/veiculos/{nome_veiculo}", response_model=VeiculoInDB)
async def excluir_veiculo(nome_veiculo: str, current_user: TokenData = Depends(get_current_user)):
    return veiculo_db.delete_veiculo(nome_veiculo)
