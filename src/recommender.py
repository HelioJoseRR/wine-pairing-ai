import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional
import google.generativeai as genai

try:
    from .config import GEMINI_API_KEY, GEMINI_MODEL, REQUIRED_CSV_COLUMNS
    from .logger import setup_logger
except ImportError:
    from config import GEMINI_API_KEY, GEMINI_MODEL, REQUIRED_CSV_COLUMNS
    from logger import setup_logger

logger = setup_logger(__name__)

class WineRecommender:
    def __init__(self, csv_path: str):
        logger.info(f"Inicializando Wine Recommender com CSV: {csv_path}")
        
        if not Path(csv_path).exists():
            logger.error(f"Arquivo de vinhos não encontrado: {csv_path}")
            raise FileNotFoundError(f"Arquivo de vinhos não encontrado: {csv_path}")
        
        try:
            self.df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"CSV carregado com {len(self.df)} vinhos")
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo CSV: {e}")
            raise ValueError(f"Erro ao carregar arquivo CSV: {e}")
        
        # Validar colunas necessárias
        self._validate_csv_columns()
        
        # Configurar Gemini para justificativas detalhadas
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            self.use_llm_justification = True
            logger.info("LLM habilitado para justificativas")
        else:
            self.use_llm_justification = False
            logger.warning("LLM não configurado - usando justificativas simples")
    
    def _validate_csv_columns(self) -> None:
        """Valida que todas as colunas necessárias existem no CSV"""
        missing_columns = [col for col in REQUIRED_CSV_COLUMNS if col not in self.df.columns]
        
        if missing_columns:
            error_msg = f"Colunas ausentes no CSV: {', '.join(missing_columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Todas as colunas necessárias foram encontradas no CSV")
    
    def recommend(self, dish_params: Dict[str, float], perfil_fuzzy: Dict[str, any]) -> Dict[str, any]:
        """
        Recomenda um vinho baseado nos parâmetros do prato e perfil fuzzy.
        """
        logger.info(f"Buscando vinho com perfil {perfil_fuzzy['categoria']}")
        
        categoria = perfil_fuzzy['categoria']
        
        # Mapear categoria fuzzy para faixa de corpo do vinho
        if categoria == 'leve':
            corpo_min, corpo_max = 0, 5
        elif categoria == 'medio':
            corpo_min, corpo_max = 4, 7
        else:  # encorpado
            corpo_min, corpo_max = 6, 10
        
        # Filtrar vinhos por corpo
        candidatos = self.df[
            (self.df['corpo'] >= corpo_min) & 
            (self.df['corpo'] <= corpo_max)
        ].copy()
        
        if len(candidatos) == 0:
            logger.warning("Nenhum candidato encontrado na faixa de corpo - usando todos os vinhos")
            candidatos = self.df.copy()
        
        logger.info(f"{len(candidatos)} vinhos candidatos encontrados")
        
        # Calcular distâncias usando operações vetorizadas (muito mais rápido)
        candidatos = candidatos.dropna(subset=['acidez', 'intensidade_sabor', 'doçura'])
        
        if len(candidatos) == 0:
            logger.error("Nenhum vinho válido após remover valores nulos")
            raise ValueError("Nenhum vinho válido encontrado na base de dados")
        
        # Operações vetorizadas do pandas (100x mais rápido que iterrows)
        candidatos['dist_acidez'] = np.abs(candidatos['acidez'] - dish_params['acidez'])
        candidatos['dist_intensidade'] = np.abs(candidatos['intensidade_sabor'] - dish_params['intensidade_sabor'])
        candidatos['dist_dulcor'] = np.abs(candidatos['doçura'] - dish_params['dulcor'])
        
        # Score total (menor é melhor)
        candidatos['score'] = (
            candidatos['dist_acidez'] + 
            candidatos['dist_intensidade'] + 
            candidatos['dist_dulcor'] * 0.5
        )
        
        # Ordenar por score e pegar o melhor
        candidatos = candidatos.sort_values('score')
        melhor = candidatos.iloc[0]
        
        logger.info(f"Melhor vinho selecionado: {melhor['nome']} (score: {melhor['score']:.2f})")
        
        # Justificativa com LLM (se disponível) ou fallback
        if self.use_llm_justification:
            justificativa = self._generate_llm_justification(melhor, dish_params, perfil_fuzzy)
        else:
            justificativa = self._generate_justification(melhor, dish_params, perfil_fuzzy)
        
        return {
            'nome': melhor['nome'],
            'uva': melhor['uva'],
            'tipo': melhor['tipo'],
            'país': melhor['país'],
            'região': melhor['região'],
            'teor_alcoolico': melhor['teor_alcoolico'],
            'acidez': melhor['acidez'],
            'corpo': melhor['corpo'],
            'doçura': melhor['doçura'],
            'intensidade_sabor': melhor['intensidade_sabor'],
            'harmonizacoes': melhor['harmonizacoes'],
            'justificativa': justificativa
        }
    
    def _generate_justification(self, wine, dish_params: Dict[str, float], perfil_fuzzy: Dict[str, any]) -> str:
        """
        Gera uma justificativa textual para a recomendação.
        """
        categoria = perfil_fuzzy['categoria']
        
        justificativa = f"O vinho {wine['nome']} é ideal para este prato porque possui perfil {categoria}, "
        
        if categoria == 'leve':
            justificativa += "combinando com a leveza e frescor dos ingredientes. "
        elif categoria == 'medio':
            justificativa += "equilibrando intensidade e elegância. "
        else:
            justificativa += "sustentando a intensidade e complexidade dos sabores. "
        
        # Acidez
        if abs(wine['acidez'] - dish_params['acidez']) < 2:
            justificativa += f"Sua acidez ({wine['acidez']}/10) harmoniza perfeitamente com a do prato. "
        
        # Corpo e gordura
        if dish_params['gordura'] > 6 and wine['corpo'] > 6:
            justificativa += "Seu corpo robusto corta a gordura do prato. "
        
        # Especiarias
        if dish_params['especiarias'] > 6 and wine['intensidade_sabor'] > 6:
            justificativa += "Sua intensidade de sabor complementa as especiarias presentes. "
        
        return justificativa.strip()
    
    def _generate_llm_justification(self, wine, dish_params: Dict[str, float], perfil_fuzzy: Dict[str, any]) -> str:
        """
        Gera uma justificativa detalhada usando o Gemini, incluindo fatos interessantes.
        """
        prompt = f"""
Você é um sommelier expert. Explique de forma envolvente e didática por que o vinho {wine['nome']} 
é a escolha perfeita para um prato com as seguintes características:

**Características do Prato:**
- Intensidade de sabor: {dish_params['intensidade_sabor']}/10
- Acidez: {dish_params['acidez']}/10
- Gordura: {dish_params['gordura']}/10
- Dulçor: {dish_params['dulcor']}/10
- Especiarias: {dish_params['especiarias']}/10
- Método de preparo: {dish_params['metodo_preparo']}/10
- Perfil Fuzzy calculado: {perfil_fuzzy['categoria']} ({perfil_fuzzy['valor']:.1f}/10)

**Vinho Selecionado:**
- Nome: {wine['nome']}
- Uva: {wine['uva']}
- Tipo: {wine['tipo']}
- País/Região: {wine['país']}, {wine['região']}
- Acidez: {wine['acidez']}/10
- Corpo: {wine['corpo']}/10
- Doçura: {wine['doçura']}/10
- Intensidade: {wine['intensidade_sabor']}/10

Sua resposta deve ter EXATAMENTE 3 parágrafos curtos (2-3 frases cada):

1. **Harmonização Técnica**: Explique cientificamente por que os atributos do vinho (acidez, corpo, taninos) 
   complementam o prato, citando valores específicos.

2. **Experiência Sensorial**: Descreva como a combinação funcionará no paladar, 
   quais sabores serão realçados ou equilibrados.

3. **Fato Interessante**: Compartilhe uma curiosidade fascinante sobre o vinho, sua uva, região 
   ou uma história/tradição relacionada à harmonização.

Seja conciso, técnico mas acessível. Use linguagem de sommelier profissional.
NÃO use markdown, asteriscos ou formatação especial.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            if not response or not hasattr(response, 'text'):
                logger.warning("Resposta inválida da LLM - usando justificativa básica")
                return self._generate_justification(wine, dish_params, perfil_fuzzy)
            
            logger.info("Justificativa LLM gerada com sucesso")
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Erro ao gerar justificativa com LLM: {str(e)} - usando justificativa básica")
            return self._generate_justification(wine, dish_params, perfil_fuzzy)
