"""
Módulo para construir árvore de decisão fuzzy e regras baseadas nos pratos conhecidos
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import skfuzzy as fuzz

try:
    from .logger import setup_logger
except ImportError:
    from logger import setup_logger

logger = setup_logger(__name__)


class FuzzyTreeNode:
    """Nó da árvore de decisão fuzzy"""
    def __init__(self, attribute=None, threshold=None, category=None, samples=None):
        self.attribute = attribute  # Nome do atributo
        self.threshold = threshold  # Valor de divisão
        self.category = category    # Categoria do vinho (leve/médio/encorpado)
        self.samples = samples or []  # Amostras neste nó
        self.left = None   # valores <= threshold
        self.right = None  # valores > threshold
        self.is_leaf = category is not None
        self.confidence = 0.0
        
    def __repr__(self, level=0):
        ret = "  " * level
        if self.is_leaf:
            ret += f"└─ LEAF: {self.category.upper()} (samples: {len(self.samples)}, conf: {self.confidence:.2f})\n"
        else:
            ret += f"├─ {self.attribute} <= {self.threshold:.2f}\n"
            if self.left:
                ret += self.left.__repr__(level + 1)
            if self.right:
                ret += "  " * level + f"└─ {self.attribute} > {self.threshold:.2f}\n"
                if self.right:
                    ret += self.right.__repr__(level + 1)
        return ret


class FuzzyRule:
    """Regra fuzzy gerada automaticamente"""
    def __init__(self, conditions: Dict[str, Tuple[str, float]], conclusion: str, confidence: float = 1.0):
        self.conditions = conditions  # {'acidez': ('alta', 7.5), 'gordura': ('baixa', 3.2)}
        self.conclusion = conclusion  # 'leve', 'medio', 'encorpado'
        self.confidence = confidence
        self.support = 0  # Quantos pratos suportam esta regra
        
    def __repr__(self):
        cond_str = " AND ".join([f"{attr}={fuzzy_val}" for attr, (fuzzy_val, _) in self.conditions.items()])
        return f"IF {cond_str} THEN {self.conclusion} (conf: {self.confidence:.2f}, supp: {self.support})"
    
    def to_text(self):
        """Retorna representação textual da regra"""
        cond_str = " E ".join([f"{attr} é {fuzzy_val}" for attr, (fuzzy_val, _) in self.conditions.items()])
        return f"SE {cond_str} ENTÃO perfil={self.conclusion}"


class FuzzyTreeBuilder:
    """Constrói árvore de decisão e regras fuzzy a partir dos pratos conhecidos"""
    
    def __init__(self, dishes_csv: str = None):
        logger.info("Inicializando Fuzzy Tree Builder")
        self.tree = None
        self.rules = []
        self.dishes_df = None
        self.feature_importance = {}
        
        # Atributos considerados para análise
        self.attributes = [
            'intensidade_sabor',
            'acidez', 
            'gordura',
            'especiarias',
            'dulcor',
            'proteina',
            'metodo_preparo'
        ]
        
        # Carregar pratos se o CSV for fornecido
        if dishes_csv and Path(dishes_csv).exists():
            self.load_dishes(dishes_csv)
    
    def load_dishes(self, csv_path: str):
        """Carrega pratos do CSV"""
        logger.info(f"Carregando pratos de {csv_path}")
        try:
            self.dishes_df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"{len(self.dishes_df)} pratos carregados")
            
            # Mapear harmonizações para categorias
            self.dishes_df['categoria_vinho'] = self.dishes_df['harmonizacao_sugerida'].apply(
                self._map_harmonization_to_category
            )
            
            logger.info(f"Distribuição: {self.dishes_df['categoria_vinho'].value_counts().to_dict()}")
        except Exception as e:
            logger.error(f"Erro ao carregar pratos: {e}")
            self.dishes_df = None
    
    def _map_harmonization_to_category(self, harmonizacao: str) -> str:
        """Mapeia texto de harmonização para categoria fuzzy"""
        harmonizacao = str(harmonizacao).lower()
        
        if any(x in harmonizacao for x in ['leve', 'light', 'espumante', 'verde']):
            return 'leve'
        elif any(x in harmonizacao for x in ['encorpado', 'robusto', 'premium', 'doce', 'fortificado']):
            return 'encorpado'
        else:
            return 'medio'
    
    def calculate_gini_impurity(self, samples: List[int]) -> float:
        """Calcula impureza de Gini para um conjunto de amostras"""
        if not samples:
            return 0.0
        
        categories = self.dishes_df.loc[samples, 'categoria_vinho']
        total = len(categories)
        
        gini = 1.0
        for cat in ['leve', 'medio', 'encorpado']:
            prob = (categories == cat).sum() / total
            gini -= prob ** 2
        
        return gini
    
    def find_best_split(self, samples: List[int], attributes: List[str]) -> Tuple[str, float, float]:
        """Encontra o melhor atributo e threshold para dividir os dados"""
        best_gain = -1
        best_attr = None
        best_threshold = None
        
        parent_gini = self.calculate_gini_impurity(samples)
        
        for attr in attributes:
            values = self.dishes_df.loc[samples, attr].values
            unique_vals = np.unique(values)
            
            # Testar thresholds nos pontos médios
            for i in range(len(unique_vals) - 1):
                threshold = (unique_vals[i] + unique_vals[i + 1]) / 2.0
                
                left_samples = [s for s in samples if self.dishes_df.loc[s, attr] <= threshold]
                right_samples = [s for s in samples if self.dishes_df.loc[s, attr] > threshold]
                
                if not left_samples or not right_samples:
                    continue
                
                # Calcular ganho de informação
                left_gini = self.calculate_gini_impurity(left_samples)
                right_gini = self.calculate_gini_impurity(right_samples)
                
                weighted_gini = (len(left_samples) * left_gini + len(right_samples) * right_gini) / len(samples)
                gain = parent_gini - weighted_gini
                
                if gain > best_gain:
                    best_gain = gain
                    best_attr = attr
                    best_threshold = threshold
        
        return best_attr, best_threshold, best_gain
    
    def build_tree(self, samples: List[int] = None, depth: int = 0, max_depth: int = 5) -> FuzzyTreeNode:
        """Constrói árvore de decisão recursivamente"""
        if self.dishes_df is None or len(self.dishes_df) == 0:
            logger.warning("Nenhum dado de prato disponível")
            return None
        
        if samples is None:
            samples = list(self.dishes_df.index)
        
        # Critérios de parada
        categories = self.dishes_df.loc[samples, 'categoria_vinho']
        
        # Se todos são da mesma categoria ou profundidade máxima atingida
        if len(categories.unique()) == 1 or depth >= max_depth or len(samples) < 3:
            category = categories.mode()[0]
            confidence = (categories == category).sum() / len(categories)
            node = FuzzyTreeNode(category=category, samples=samples)
            node.confidence = confidence
            return node
        
        # Encontrar melhor split
        attr, threshold, gain = self.find_best_split(samples, self.attributes)
        
        if attr is None or gain < 0.01:
            # Não há split útil, criar folha
            category = categories.mode()[0]
            confidence = (categories == category).sum() / len(categories)
            node = FuzzyTreeNode(category=category, samples=samples)
            node.confidence = confidence
            return node
        
        # Criar nó interno
        node = FuzzyTreeNode(attribute=attr, threshold=threshold, samples=samples)
        
        # Atualizar importância do atributo
        self.feature_importance[attr] = self.feature_importance.get(attr, 0) + gain
        
        # Dividir amostras
        left_samples = [s for s in samples if self.dishes_df.loc[s, attr] <= threshold]
        right_samples = [s for s in samples if self.dishes_df.loc[s, attr] > threshold]
        
        # Recursão
        node.left = self.build_tree(left_samples, depth + 1, max_depth)
        node.right = self.build_tree(right_samples, depth + 1, max_depth)
        
        return node
    
    def extract_rules_from_tree(self, node: FuzzyTreeNode = None, conditions: Dict = None) -> List[FuzzyRule]:
        """Extrai regras da árvore de decisão"""
        if node is None:
            node = self.tree
            conditions = {}
            self.rules = []
        
        if node.is_leaf:
            # Fuzzificar condições
            fuzzy_conditions = {}
            for attr, threshold in conditions.items():
                fuzzy_val = self._fuzzify_value(attr, threshold)
                fuzzy_conditions[attr] = (fuzzy_val, threshold)
            
            rule = FuzzyRule(fuzzy_conditions, node.category, node.confidence)
            rule.support = len(node.samples)
            self.rules.append(rule)
        else:
            # Explorar ramo esquerdo (<=)
            if node.left:
                new_conditions = conditions.copy()
                new_conditions[node.attribute] = node.threshold
                self.extract_rules_from_tree(node.left, new_conditions)
            
            # Explorar ramo direito (>)
            if node.right:
                new_conditions = conditions.copy()
                new_conditions[node.attribute] = node.threshold + 0.1
                self.extract_rules_from_tree(node.right, new_conditions)
        
        return self.rules
    
    def _fuzzify_value(self, attribute: str, value: float) -> str:
        """Converte valor numérico em termo fuzzy (baixo/medio/alto)"""
        # Tratamento especial para acidez que usa "baixa/media/alta"
        if attribute == 'acidez':
            if value < 4:
                return 'baixa'
            elif value < 7:
                return 'media'
            else:
                return 'alta'
        elif attribute == 'gordura':
            if value < 4:
                return 'baixa'
            elif value < 7:
                return 'media'
            else:
                return 'alta'
        elif attribute == 'proteina':
            if value < 4:
                return 'baixa'
            elif value < 7:
                return 'media'
            else:
                return 'alta'
        else:
            # Para outros atributos: baixo/medio/alto
            if value < 4:
                return 'baixo'
            elif value < 7:
                return 'medio'
            else:
                return 'alto'
    
    def train(self, max_depth: int = 5):
        """Treina o modelo: constrói árvore e extrai regras"""
        logger.info("Iniciando treinamento do modelo fuzzy")
        
        if self.dishes_df is None:
            logger.error("Nenhum dado disponível para treinamento")
            return
        
        # Construir árvore
        logger.info(f"Construindo árvore (max_depth={max_depth})")
        self.tree = self.build_tree(max_depth=max_depth)
        
        # Extrair regras
        logger.info("Extraindo regras da árvore")
        self.rules = self.extract_rules_from_tree()
        
        # Filtrar regras redundantes
        self.rules = self._remove_redundant_rules(self.rules)
        
        logger.info(f"Treinamento concluído: {len(self.rules)} regras geradas")
        
        return self.tree, self.rules
    
    def _remove_redundant_rules(self, rules: List[FuzzyRule]) -> List[FuzzyRule]:
        """Remove regras redundantes mantendo as de maior confiança"""
        unique_rules = {}
        
        for rule in rules:
            key = (frozenset(rule.conditions.items()), rule.conclusion)
            if key not in unique_rules or rule.confidence > unique_rules[key].confidence:
                unique_rules[key] = rule
        
        return list(unique_rules.values())
    
    def predict(self, params: Dict[str, float]) -> Dict[str, any]:
        """Faz predição usando a árvore"""
        if self.tree is None:
            logger.warning("Árvore não foi treinada")
            return {'categoria': 'medio', 'confidence': 0.5}
        
        node = self.tree
        
        while not node.is_leaf:
            attr_value = params.get(node.attribute, 5.0)
            if attr_value <= node.threshold:
                node = node.left
            else:
                node = node.right
        
        return {
            'categoria': node.category,
            'confidence': node.confidence,
            'samples': len(node.samples)
        }
    
    def get_tree_visualization(self) -> str:
        """Retorna visualização em texto da árvore"""
        if self.tree is None:
            return "Árvore não construída"
        
        return str(self.tree)
    
    def get_rules_text(self) -> List[str]:
        """Retorna lista de regras em formato texto"""
        if not self.rules:
            return ["Nenhuma regra disponível"]
        
        # Ordenar por confiança e suporte
        sorted_rules = sorted(self.rules, key=lambda r: (r.confidence, r.support), reverse=True)
        
        return [f"{i+1}. {rule.to_text()} - Confiança: {rule.confidence:.2f}, Suporte: {rule.support} pratos"
                for i, rule in enumerate(sorted_rules)]
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do modelo"""
        if not self.dishes_df is not None:
            return {}
        
        stats = {
            'total_pratos': len(self.dishes_df),
            'total_regras': len(self.rules),
            'distribuicao_categorias': self.dishes_df['categoria_vinho'].value_counts().to_dict(),
            'importancia_atributos': sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True),
            'profundidade_arvore': self._calculate_tree_depth(self.tree) if self.tree else 0
        }
        
        return stats
    
    def _calculate_tree_depth(self, node: FuzzyTreeNode) -> int:
        """Calcula profundidade da árvore"""
        if node is None or node.is_leaf:
            return 0
        
        left_depth = self._calculate_tree_depth(node.left) if node.left else 0
        right_depth = self._calculate_tree_depth(node.right) if node.right else 0
        
        return 1 + max(left_depth, right_depth)
