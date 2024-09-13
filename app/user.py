# Adiciona usuarios ao credentials.txt
from app.auth import get_password_hash
import os

def adicionar_usuario(username: str, password: str, file_path: str = "credentials.txt"):
    hashed_password = get_password_hash(password)

    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                lines = file.readlines()
        else:
            lines = []

        # Verifica se o usuário já existe
        if any(line.startswith(f"{username}:") for line in lines):
            raise ValueError("Usuário já existe")

        # Adiciona o novo usuário ao final do arquivo
        with open(file_path, "a") as file:
            file.write(f"{username}:{hashed_password}\n")
        print(f"Usuário {username} adicionado com sucesso")
    except ValueError as e:
        print(f"Erro: {e}")
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}")
    except IOError as e:
        print(f"Erro ao acessar o arquivo: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Exemplo de uso
username = "user3"
password = "password3"
adicionar_usuario(username, password)
