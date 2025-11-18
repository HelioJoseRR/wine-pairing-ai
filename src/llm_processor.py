import json
from typing import Dict
import google.generativeai as genai
from pathlib import Path

try:
    from .config import GEMINI_API_KEY, GEMINI_MODEL, REQUIRED_DISH_PARAMS
    from .logger import setup_logger
    from .cache import LLMCache
except ImportError:
    from config import GEMINI_API_KEY, GEMINI_MODEL, REQUIRED_DISH_PARAMS
    from logger import setup_logger
    from cache import LLMCache

logger = setup_logger(__name__)

class LLMProcessor:
    def __init__(self, use_cache: bool = True):
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY não encontrada no arquivo .env")
            raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Configurar cache
        self.use_cache = use_cache
        if use_cache:
            cache_dir = Path(__file__).parent.parent / ".cache"
            cache_file = cache_dir / "llm_cache.json"
            self.cache = LLMCache(str(cache_file))
            logger.info("Cache LLM ativado")
        else:
            self.cache = None
        
        logger.info(f"LLM Processor inicializado com modelo {GEMINI_MODEL}")
    
    def analyze_dish(self, dish_description: str) -> Dict[str, float]:
        # Verificar cache
        if self.use_cache and self.cache:
            cached_result = self.cache.get(dish_description)
            if cached_result:
                logger.info("Resultado recuperado do cache")
                return cached_result
        
        logger.info(f"Analisando prato: {dish_description[:50]}...")
        
        prompt = f"""
Analise o seguinte prato e retorne EXATAMENTE um objeto JSON válido com os 10 parâmetros abaixo.
Use valores numéricos de 0 a 10 para cada parâmetro.

Prato: {dish_description}

Retorne apenas o JSON, sem texto adicional, no seguinte formato:
{{
    "proteina": <0-10>,
    "gordura": <0-10>,
    "acidez": <0-10>,
    "dulcor": <0-10>,
    "intensidade_sabor": <0-10>,
    "crocancia": <0-10>,
    "metodo_preparo": <0-10, onde 0=cru, 5=cozido, 10=grelhado/defumado>,
    "especiarias": <0-10>,
    "teor_umami": <0-10>,
    "nivel_salgado": <0-10>
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Validar que a resposta existe
            if not response or not hasattr(response, 'text'):
                logger.error("Resposta vazia da API Gemini")
                raise ValueError("Resposta vazia da API Gemini")
            
            text = response.text.strip()
            
            # Remove markdown code blocks se existirem
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            text = text.strip()
            
            # Parse JSON
            params = json.loads(text)
            
            # Validação usando config
            for key in REQUIRED_DISH_PARAMS:
                if key not in params:
                    logger.error(f"Parâmetro {key} não encontrado na resposta da LLM")
                    raise ValueError(f"Parâmetro {key} não encontrado na resposta da LLM")
                
                # Validar que o valor é numérico
                try:
                    value = float(params[key])
                except (TypeError, ValueError):
                    logger.error(f"Parâmetro {key} não é numérico: {params[key]}")
                    raise ValueError(f"Parâmetro {key} não é numérico: {params[key]}")
                
                # Garantir valores entre 0 e 10
                params[key] = max(0.0, min(10.0, value))
            
            # Salvar no cache
            if self.use_cache and self.cache:
                self.cache.set(dish_description, params)
            
            logger.info("Análise do prato concluída com sucesso")
            return params
            
        except json.JSONDecodeError as e:
            response_preview = text[:200] if 'text' in locals() and text else "N/A"
            error_msg = f"Erro ao parsear JSON da LLM: {e}\nResposta: {response_preview}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Erro ao processar resposta da LLM: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

