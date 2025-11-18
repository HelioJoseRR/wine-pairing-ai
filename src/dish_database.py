"""
Módulo para gerenciamento da base de dados de pratos
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

try:
    from .logger import setup_logger
except ImportError:
    from logger import setup_logger

logger = setup_logger(__name__)

class DishDatabase:
    """Gerencia a base de dados de pratos pré-cadastrados"""
    
    def __init__(self, csv_path: str):
        logger.info(f"Carregando base de pratos: {csv_path}")
        
        if not Path(csv_path).exists():
            logger.warning(f"Arquivo de pratos não encontrado: {csv_path}")
            self.df = pd.DataFrame()
            return
        
        try:
            self.df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"Base de pratos carregada: {len(self.df)} pratos")
        except Exception as e:
            logger.error(f"Erro ao carregar CSV de pratos: {e}")
            self.df = pd.DataFrame()
    
    def search_dish(self, query: str) -> List[Dict]:
        """
        Busca pratos na base de dados por nome ou ingredientes
        """
        if self.df.empty:
            return []
        
        query_lower = query.lower()
        
        # Busca por nome
        mask_nome = self.df['nome'].str.lower().str.contains(query_lower, na=False)
        
        # Busca por ingredientes
        mask_ingredientes = self.df['ingredientes_principais'].str.lower().str.contains(query_lower, na=False)
        
        # Combina as buscas
        results = self.df[mask_nome | mask_ingredientes]
        
        if len(results) == 0:
            logger.info(f"Nenhum prato encontrado para: {query}")
            return []
        
        logger.info(f"{len(results)} prato(s) encontrado(s)")
        
        # Converte para lista de dicionários
        return results.to_dict('records')
    
    def get_dish_by_name(self, name: str) -> Optional[Dict]:
        """
        Recupera um prato específico pelo nome exato
        """
        if self.df.empty:
            return None
        
        result = self.df[self.df['nome'].str.lower() == name.lower()]
        
        if len(result) == 0:
            return None
        
        return result.iloc[0].to_dict()
    
    def list_categories(self) -> List[str]:
        """
        Lista todas as categorias de pratos disponíveis
        """
        if self.df.empty:
            return []
        
        return sorted(self.df['categoria'].unique().tolist())
    
    def list_dishes_by_category(self, category: str) -> List[Dict]:
        """
        Lista todos os pratos de uma categoria
        """
        if self.df.empty:
            return []
        
        results = self.df[self.df['categoria'].str.lower() == category.lower()]
        return results.to_dict('records')
    
    def get_all_dishes(self) -> List[Dict]:
        """
        Retorna todos os pratos da base
        """
        if self.df.empty:
            return []
        
        return self.df.to_dict('records')
    
    def extract_parameters(self, dish: Dict) -> Dict[str, float]:
        """
        Extrai os 10 parâmetros de um prato do CSV
        """
        return {
            'proteina': float(dish.get('proteina', 5)),
            'gordura': float(dish.get('gordura', 5)),
            'acidez': float(dish.get('acidez', 5)),
            'dulcor': float(dish.get('dulcor', 5)),
            'intensidade_sabor': float(dish.get('intensidade_sabor', 5)),
            'crocancia': float(dish.get('crocancia', 5)),
            'metodo_preparo': float(dish.get('metodo_preparo', 5)),
            'especiarias': float(dish.get('especiarias', 5)),
            'teor_umami': float(dish.get('teor_umami', 5)),
            'nivel_salgado': float(dish.get('nivel_salgado', 5))
        }
