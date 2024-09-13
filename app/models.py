from pydantic import BaseModel, field_validator
from typing import Optional

class Veiculo(BaseModel):
    nome: str
    modelo: str
    status: str

    @field_validator('nome')
    def nome_nao_vazio(cls, v):
        if not v:
            raise ValueError('Nome não pode ser vazio')
        return v

    @field_validator('status')
    def status_valido(cls, v):
        status_validos = ["CONECTADO", "DESCONECTADO"]
        if v not in status_validos:
            raise ValueError('Status inválido')
        return v
    
class VeiculoInDB(Veiculo):
    id: int

class StatusUpdate(BaseModel):
    status: str
