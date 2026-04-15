from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
import math
import os

# --- Configuração do Banco de Dados (Nível Intermediário) ---
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./calculadora.db")
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CalculoDB(Base):
    __tablename__ = "calculos"
    id = Column(Integer, primary_key=True, index=True)
    operacao = Column(String)
    numero1 = Column(Float)
    numero2 = Column(Float, nullable=True)
    resultado = Column(Float)
    data_hora = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- Dependência do Banco de Dados ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Instância da API ---
app = FastAPI(
    title="Calculadora API - Nível Intermediário",
    description="API de Calculadora com SQLite, Histórico e Novas Operações",
    version="2.0.0"
)

# --- Configuração de CORS (Nível Intermediário) ---
cors_origins_env = os.getenv("CORS_ORIGINS", "*").strip()
cors_origins = ["*"] if cors_origins_env == "*" else [o.strip() for o in cors_origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Dados ---
class OperacaoDoisNumerosRequest(BaseModel):
    numero1: float
    numero2: float

class OperacaoUmNumeroRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    numero1: float

class OperacaoUpdate(BaseModel):
    numero1: float | None = None
    numero2: float | None = None
    operacao: str | None = None
    resultado: float | None = None

class ResultadoResponse(BaseModel):
    operacao: str
    numero1: float
    numero2: float | None
    resultado: float
    data_hora: datetime.datetime

class CalculoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    operacao: str
    numero1: float
    numero2: float | None
    resultado: float
    data_hora: datetime.datetime

# --- Função Auxiliar para Salvar Histórico ---
def salvar_historico(db: Session, operacao: str, n1: float, n2: float | None, res: float):
    db_calculo = CalculoDB(operacao=operacao, numero1=n1, numero2=n2, resultado=res)
    db.add(db_calculo)
    db.commit()
    db.refresh(db_calculo)
    return db_calculo

# --- Endpoints ---

@app.get("/")
def raiz():
    return {"mensagem": "Bem-vindo a Calculadora API Intermediária!", "docs": "/docs"}

@app.get("/historico", response_model=list[CalculoResponse])
def ver_historico(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return (
        db.query(CalculoDB)
        .order_by(CalculoDB.data_hora.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

@app.put("/historico/{id}", response_model=CalculoResponse)
def atualizar_calculo(id: int, dados: OperacaoUpdate, db: Session = Depends(get_db)):
    db_calculo = db.query(CalculoDB).filter(CalculoDB.id == id).first()
    if not db_calculo:
        raise HTTPException(status_code=404, detail="Calculo nao encontrado")
    
    update_data = dados.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_calculo, key, value)
    
    db.commit()
    db.refresh(db_calculo)
    return db_calculo

@app.delete("/historico/{id}")
def deletar_calculo(id: int, db: Session = Depends(get_db)):
    db_calculo = db.query(CalculoDB).filter(CalculoDB.id == id).first()
    if not db_calculo:
        raise HTTPException(status_code=404, detail="Calculo nao encontrado")
    db.delete(db_calculo)
    db.commit()
    return {"mensagem": "Calculo deletado com sucesso"}

@app.delete("/historico")
def limpar_historico(db: Session = Depends(get_db)):
    db.query(CalculoDB).delete()
    db.commit()
    return {"mensagem": "Historico limpo com sucesso"}

@app.post("/somar", response_model=ResultadoResponse)
def somar(dados: OperacaoDoisNumerosRequest, db: Session = Depends(get_db)):
    resultado = dados.numero1 + dados.numero2
    db_calculo = salvar_historico(db, "soma", dados.numero1, dados.numero2, resultado)
    return ResultadoResponse(
        operacao="soma",
        numero1=dados.numero1,
        numero2=dados.numero2,
        resultado=resultado,
        data_hora=db_calculo.data_hora
    )

@app.post("/subtrair", response_model=ResultadoResponse)
def subtrair(dados: OperacaoDoisNumerosRequest, db: Session = Depends(get_db)):
    resultado = dados.numero1 - dados.numero2
    db_calculo = salvar_historico(db, "subtracao", dados.numero1, dados.numero2, resultado)
    return ResultadoResponse(
        operacao="subtracao",
        numero1=dados.numero1,
        numero2=dados.numero2,
        resultado=resultado,
        data_hora=db_calculo.data_hora
    )

@app.post("/multiplicar", response_model=ResultadoResponse)
def multiplicar(dados: OperacaoDoisNumerosRequest, db: Session = Depends(get_db)):
    resultado = dados.numero1 * dados.numero2
    db_calculo = salvar_historico(db, "multiplicacao", dados.numero1, dados.numero2, resultado)
    return ResultadoResponse(
        operacao="multiplicacao",
        numero1=dados.numero1,
        numero2=dados.numero2,
        resultado=resultado,
        data_hora=db_calculo.data_hora
    )

@app.post("/dividir", response_model=ResultadoResponse)
def dividir(dados: OperacaoDoisNumerosRequest, db: Session = Depends(get_db)):
    if dados.numero2 == 0:
        raise HTTPException(status_code=400, detail="Divisao por zero nao e permitida!")
    resultado = dados.numero1 / dados.numero2
    db_calculo = salvar_historico(db, "divisao", dados.numero1, dados.numero2, resultado)
    return ResultadoResponse(
        operacao="divisao",
        numero1=dados.numero1,
        numero2=dados.numero2,
        resultado=resultado,
        data_hora=db_calculo.data_hora
    )

@app.post("/potencia", response_model=ResultadoResponse)
def potencia(dados: OperacaoDoisNumerosRequest, db: Session = Depends(get_db)):
    resultado = math.pow(dados.numero1, dados.numero2)
    db_calculo = salvar_historico(db, "potencia", dados.numero1, dados.numero2, resultado)
    return ResultadoResponse(
        operacao="potencia",
        numero1=dados.numero1,
        numero2=dados.numero2,
        resultado=resultado,
        data_hora=db_calculo.data_hora
    )

@app.post("/raiz", response_model=ResultadoResponse)
def raiz_quadrada(dados: OperacaoUmNumeroRequest, db: Session = Depends(get_db)):
    if dados.numero1 < 0:
        raise HTTPException(status_code=400, detail="Raiz quadrada de numero negativo nao permitida no conjunto dos reais!")
    resultado = math.sqrt(dados.numero1)
    db_calculo = salvar_historico(db, "raiz", dados.numero1, None, resultado)
    return ResultadoResponse(
        operacao="raiz",
        numero1=dados.numero1,
        numero2=None,
        resultado=resultado,
        data_hora=db_calculo.data_hora
    )

@app.get("/operacoes")
def listar_operacoes():
    return {
        "post": [
            {"endpoint": "/somar", "operacao": "soma", "usa_numero2": True},
            {"endpoint": "/subtrair", "operacao": "subtracao", "usa_numero2": True},
            {"endpoint": "/multiplicar", "operacao": "multiplicacao", "usa_numero2": True},
            {"endpoint": "/dividir", "operacao": "divisao", "usa_numero2": True},
            {"endpoint": "/potencia", "operacao": "potencia", "usa_numero2": True},
            {"endpoint": "/raiz", "operacao": "raiz", "usa_numero2": False},
        ],
        "get": [
            {"endpoint": "/calcular", "operacoes": ["soma", "subtracao", "multiplicacao", "divisao", "potencia", "raiz"]},
            {"endpoint": "/historico", "descricao": "lista historico com paginacao (limit/offset)"},
        ],
    }

@app.get("/calcular")
def calcular_query(numero1: float, operacao: str, numero2: float | None = None, db: Session = Depends(get_db)):
    operacoes = {
        "soma": lambda a, b: a + b,
        "subtracao": lambda a, b: a - b,
        "multiplicacao": lambda a, b: a * b,
        "divisao": lambda a, b: a / b,
        "potencia": lambda a, b: math.pow(a, b),
        "raiz": lambda a, b: math.sqrt(a)
    }
    if operacao not in operacoes:
        raise HTTPException(
            status_code=400,
            detail=f"Operacao invalida. Use: {list(operacoes.keys())}"
        )
    if operacao != "raiz" and numero2 is None:
        raise HTTPException(status_code=400, detail="numero2 e obrigatorio para esta operacao!")
    if operacao == "divisao" and numero2 == 0:
        raise HTTPException(status_code=400, detail="Divisao por zero!")
    if operacao == "raiz" and numero1 < 0:
        raise HTTPException(status_code=400, detail="Raiz de numero negativo!")

    resultado = operacoes[operacao](numero1, numero2)
    salvar_historico(db, operacao, numero1, numero2 if operacao != "raiz" else None, resultado)
    
    return {
        "operacao": operacao,
        "numero1": numero1,
        "numero2": numero2 if operacao != "raiz" else None,
        "resultado": resultado
    }
