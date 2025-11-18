import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMProcessor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")
        genai.configure(api_key=api_key)
        # Usa o modelo flash mais recente e rápido
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def analyze_dish(self, dish_description: str) -> dict:
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
            
            # Validação básica
            required_keys = [
                "proteina", "gordura", "acidez", "dulcor", "intensidade_sabor",
                "crocancia", "metodo_preparo", "especiarias", "teor_umami", "nivel_salgado"
            ]
            
            for key in required_keys:
                if key not in params:
                    raise ValueError(f"Parâmetro {key} não encontrado na resposta da LLM")
                # Garantir valores entre 0 e 10
                params[key] = max(0, min(10, float(params[key])))
            
            return params
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao parsear JSON da LLM: {e}\nResposta: {text}")
        except Exception as e:
            raise ValueError(f"Erro ao processar resposta da LLM: {e}")
