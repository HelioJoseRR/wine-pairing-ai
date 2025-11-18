"""
Configurações centralizadas do sistema
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Modelo LLM
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validações
MAX_DISH_DESCRIPTION_LENGTH = 500
MIN_DISH_DESCRIPTION_LENGTH = 5

# Colunas esperadas no CSV
REQUIRED_CSV_COLUMNS = [
    'nome', 'uva', 'tipo', 'país', 'região', 'teor_alcoolico',
    'acidez', 'corpo', 'doçura', 'intensidade_sabor', 'harmonizacoes'
]

# Parâmetros de análise do prato
REQUIRED_DISH_PARAMS = [
    "proteina", "gordura", "acidez", "dulcor", "intensidade_sabor",
    "crocancia", "metodo_preparo", "especiarias", "teor_umami", "nivel_salgado"
]
