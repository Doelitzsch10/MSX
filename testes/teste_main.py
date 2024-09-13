import unittest
from fastapi.testclient import TestClient
from app.main import app, veiculo_db
from app.models import Veiculo

client = TestClient(app)

def autenticar():
    """Função para obter o token de autenticação"""
    response = client.post("/token", json={"username": "user3", "password": "password3"})
    assert response.status_code == 200
    return response.json()["access_token"]

class TestAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Configura o token de autenticação antes dos testes"""
        cls.token = autenticar()

    def setUp(self):
        """Configura o banco de dados para os testes"""
        veiculo_db.veiculos = []
        veiculo_db.next_id = 1
        veiculo_db.add_veiculo(Veiculo(nome="Fusca", modelo="Volkswagen Fusca", status="CONECTADO"))

    def test_listar_veiculos(self):
        """Teste para verificar a listagem de veículos."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get("/veiculos", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_criar_veiculo(self):
        """Teste para criar um novo veículo."""
        headers = {"Authorization": f"Bearer {self.token}"}
        novo_veiculo = {
            "nome": "Tesla",
            "modelo": "Tesla Model S",
            "status": "CONECTADO"
        }
        response = client.post("/veiculos", json=novo_veiculo, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nome"], "Tesla")

    def test_criar_veiculo_dados_invalidos(self):
        """Teste para criar um novo veículo com dados inválidos."""
        headers = {"Authorization": f"Bearer {self.token}"}
        veiculo_invalido = {
            "nome": "",  # Nome vazio é inválido
            "modelo": "Modelo Inválido",
            "status": "DESCONHECIDO"  # Status inválido
        }
        response = client.post("/veiculos", json=veiculo_invalido, headers=headers)
        self.assertEqual(response.status_code, 422)  # Ajuste para o status code correto


    def test_obter_veiculo_por_nome(self):
        """Teste para obter um veículo existente por nome."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get("/veiculos/Fusca", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nome"], "Fusca")

    def test_obter_veiculo_nao_existente(self):
        """Teste para erro 404 ao tentar obter um veículo inexistente."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get("/veiculos/VeiculoInexistente", headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_atualizar_status_veiculo(self):
        """Teste para atualizar o status de um veículo."""
        headers = {"Authorization": f"Bearer {self.token}"}
        status_update = {"status": "DESCONECTADO"}
        response = client.put("/veiculos/Fusca", json=status_update, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "DESCONECTADO")

    def test_atualizar_status_veiculo_dados_invalidos(self):
        """Teste para atualizar o status de um veículo com dados inválidos."""
        headers = {"Authorization": f"Bearer {self.token}"}
        status_update_invalido = {"status": "INEXISTENTE"}  # Status inválido
        response = client.put("/veiculos/Fusca", json=status_update_invalido, headers=headers)
        self.assertEqual(response.status_code, 400)  # Ou o código de status apropriado para dados inválidos

    def test_excluir_veiculo(self):
        """Teste para excluir um veículo existente."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.delete("/veiculos/Fusca", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nome"], "Fusca")

    def test_excluir_veiculo_nao_existente(self):
        """Teste para erro 404 ao tentar excluir um veículo inexistente."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.delete("/veiculos/VeiculoInexistente", headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_criar_veiculos_em_massa(self):
        """Teste básico de carga criando vários veículos."""
        headers = {"Authorization": f"Bearer {self.token}"}
        for i in range(100):  # Criar 100 veículos para testar o desempenho
            novo_veiculo = {
                "nome": f"Veiculo{i}",
                "modelo": f"Modelo{i}",
                "status": "CONECTADO"
            }
            response = client.post("/veiculos", json=novo_veiculo, headers=headers)
            self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
