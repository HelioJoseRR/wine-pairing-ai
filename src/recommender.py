import pandas as pd
import numpy as np
from pathlib import Path
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class WineRecommender:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        
        # Configurar Gemini para justificativas detalhadas
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.use_llm_justification = True
        else:
            self.use_llm_justification = False
    
    def recommend(self, dish_params: dict, perfil_fuzzy: dict) -> dict:
        """
        Recomenda um vinho baseado nos parâmetros do prato e perfil fuzzy.
        """
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
        ]
        
        if len(candidatos) == 0:
            candidatos = self.df
        
        # Calcular distância entre atributos do prato e do vinho
        # Parâmetros relevantes: acidez, intensidade_sabor
        melhores_scores = []
        
        for idx, wine in candidatos.iterrows():
            # Distância euclidiana simplificada
            dist_acidez = abs(wine['acidez'] - dish_params['acidez'])
            dist_intensidade = abs(wine['intensidade_sabor'] - dish_params['intensidade_sabor'])
            
            # Fator de dulçor: pratos mais doces combinam com vinhos mais doces
            dist_dulcor = abs(wine['doçura'] - dish_params['dulcor'])
            
            # Score total (menor é melhor)
            score = dist_acidez + dist_intensidade + dist_dulcor * 0.5
            
            melhores_scores.append({
                'idx': idx,
                'score': score,
                'wine': wine
            })
        
        # Ordenar por menor score
        melhores_scores.sort(key=lambda x: x['score'])
        
        # Pegar o melhor vinho
        melhor = melhores_scores[0]['wine']
        
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
    
    def _generate_justification(self, wine, dish_params, perfil_fuzzy) -> str:
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
    
    def _generate_llm_justification(self, wine, dish_params, perfil_fuzzy) -> str:
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
            return response.text.strip()
        except Exception as e:
            # Fallback para justificativa simples se a API falhar
            return self._generate_justification(wine, dish_params, perfil_fuzzy)
