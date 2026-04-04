# Calculadora API - Sistemas Distribuídos

Projeto Avaliativo desenvolvido para disciplina Programação de Sistemas Distribuidos da Universidade do Grandes Lagos - UNILAGO sob supervisão do Professor [Gleydes Oliveira](https://github.com/gleydes).

Este projeto consiste em uma API de calculadora funcional com histórico persistente em SQLite, suporte a CORS e uma interface Frontend simples.

## 🚀 Funcionalidades

- **Operações Básicas**: Soma, Subtração, Multiplicação e Divisão.
- **Operações Intermediárias**: Potência e Raiz Quadrada.
- **Histórico**: Armazenamento de todos os cálculos em banco de dados SQLite.
- **Interface Web**: Frontend funcional em HTML/JS para realizar cálculos visualmente.
- **CRUD de Histórico**: Endpoints para listar, atualizar e deletar registros do histórico.

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **FastAPI**: Framework web moderno e rápido.
- **SQLAlchemy**: ORM para manipulação do banco de dados SQLite.
- **Uvicorn**: Servidor ASGI para rodar a aplicação.
- **Pydantic**: Validação de dados e modelos.

## ⚙️ Como Rodar o Projeto

1. **Clonar o repositório**:
   ```bash
   git clone <url-do-seu-repositorio>
   cd calculadora-api
   ```

2. **Criar e ativar o ambiente virtual**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Iniciar o servidor**:
   ```bash
   python -m uvicorn main:app --reload
   ```

5. **Acessar o sistema**:
   - **API**: [http://localhost:8000](http://localhost:8000)
   - **Documentação (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Frontend**: Abra o arquivo `index.html` no seu navegador.

## 🧪 Testes

Você pode rodar o script de testes automatizados para validar todos os endpoints:
```bash
python test_client.py
```

---
Desenvolvido por [Seu Nome]
