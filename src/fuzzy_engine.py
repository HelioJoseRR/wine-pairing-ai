import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from typing import Dict, List
from pathlib import Path

try:
    from .logger import setup_logger
    from .fuzzy_tree_builder import FuzzyTreeBuilder
except ImportError:
    from logger import setup_logger
    from fuzzy_tree_builder import FuzzyTreeBuilder

logger = setup_logger(__name__)

class FuzzyEngine:
    def __init__(self, dishes_csv: str = None, use_learned_rules: bool = True):
        logger.info("Inicializando Fuzzy Engine")
        
        self.use_learned_rules = use_learned_rules
        self.tree_builder = None
        self.learned_rules = []
        self.required_inputs = set()  # Rastreia quais inputs são necessários
        
        # Variáveis de entrada
        self.intensidade_sabor = ctrl.Antecedent(np.arange(0, 11, 1), 'intensidade_sabor')
        self.acidez = ctrl.Antecedent(np.arange(0, 11, 1), 'acidez')
        self.gordura = ctrl.Antecedent(np.arange(0, 11, 1), 'gordura')
        self.especiarias = ctrl.Antecedent(np.arange(0, 11, 1), 'especiarias')
        self.dulcor = ctrl.Antecedent(np.arange(0, 11, 1), 'dulcor')
        self.proteina = ctrl.Antecedent(np.arange(0, 11, 1), 'proteina')
        self.metodo_preparo = ctrl.Antecedent(np.arange(0, 11, 1), 'metodo_preparo')
        
        # Variável de saída
        self.perfil_vinho = ctrl.Consequent(np.arange(0, 11, 1), 'perfil_vinho')
        
        # Funções de pertinência para intensidade_sabor
        self.intensidade_sabor['baixo'] = fuzz.trimf(self.intensidade_sabor.universe, [0, 0, 5])
        self.intensidade_sabor['medio'] = fuzz.trimf(self.intensidade_sabor.universe, [3, 5, 7])
        self.intensidade_sabor['alto'] = fuzz.trimf(self.intensidade_sabor.universe, [5, 10, 10])
        
        # Funções de pertinência para acidez
        self.acidez['baixa'] = fuzz.trimf(self.acidez.universe, [0, 0, 5])
        self.acidez['media'] = fuzz.trimf(self.acidez.universe, [3, 5, 7])
        self.acidez['alta'] = fuzz.trimf(self.acidez.universe, [5, 10, 10])
        
        # Funções de pertinência para gordura
        self.gordura['baixa'] = fuzz.trimf(self.gordura.universe, [0, 0, 5])
        self.gordura['media'] = fuzz.trimf(self.gordura.universe, [3, 5, 7])
        self.gordura['alta'] = fuzz.trimf(self.gordura.universe, [5, 10, 10])
        
        # Funções de pertinência para especiarias
        self.especiarias['baixo'] = fuzz.trimf(self.especiarias.universe, [0, 0, 5])
        self.especiarias['medio'] = fuzz.trimf(self.especiarias.universe, [3, 5, 7])
        self.especiarias['alto'] = fuzz.trimf(self.especiarias.universe, [5, 10, 10])
        
        # Funções de pertinência para dulcor
        self.dulcor['baixo'] = fuzz.trimf(self.dulcor.universe, [0, 0, 4])
        self.dulcor['medio'] = fuzz.trimf(self.dulcor.universe, [3, 5, 7])
        self.dulcor['alto'] = fuzz.trimf(self.dulcor.universe, [6, 10, 10])
        
        # Funções de pertinência para proteina
        self.proteina['baixa'] = fuzz.trimf(self.proteina.universe, [0, 0, 5])
        self.proteina['media'] = fuzz.trimf(self.proteina.universe, [3, 5, 7])
        self.proteina['alta'] = fuzz.trimf(self.proteina.universe, [5, 10, 10])
        
        # Funções de pertinência para metodo_preparo
        self.metodo_preparo['baixo'] = fuzz.trimf(self.metodo_preparo.universe, [0, 0, 5])
        self.metodo_preparo['medio'] = fuzz.trimf(self.metodo_preparo.universe, [3, 5, 7])
        self.metodo_preparo['alto'] = fuzz.trimf(self.metodo_preparo.universe, [5, 10, 10])
        
        # Funções de pertinência para perfil do vinho
        self.perfil_vinho['leve'] = fuzz.trimf(self.perfil_vinho.universe, [0, 0, 5])
        self.perfil_vinho['medio'] = fuzz.trimf(self.perfil_vinho.universe, [3, 5, 7])
        self.perfil_vinho['encorpado'] = fuzz.trimf(self.perfil_vinho.universe, [5, 10, 10])
        
        # Se CSV de pratos fornecido, aprender regras
        if use_learned_rules and dishes_csv and Path(dishes_csv).exists():
            self._learn_rules_from_dishes(dishes_csv)
        else:
            self._use_default_rules()
        
        # Sistema de controle
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)
        
        # Detectar quais inputs são realmente necessários
        self._detect_required_inputs()
        
        logger.info(f"Fuzzy Engine inicializado com {len(self.rules)} regras")
        logger.info(f"Inputs necessários: {self.required_inputs}")
    
    def _detect_required_inputs(self):
        """Detecta quais antecedentes são necessários baseado nas regras"""
        # Inputs básicos que sempre estão presentes
        self.required_inputs = {'intensidade_sabor', 'acidez', 'gordura', 'especiarias', 'dulcor'}
        
        # Verificar se alguma regra usa proteina ou metodo_preparo
        for rule in self.rules:
            rule_str = str(rule)
            if 'proteina' in rule_str.lower():
                self.required_inputs.add('proteina')
            if 'metodo_preparo' in rule_str.lower():
                self.required_inputs.add('metodo_preparo')
    
    def _learn_rules_from_dishes(self, dishes_csv: str):
        """Aprende regras automaticamente dos pratos conhecidos"""
        logger.info("Aprendendo regras dos pratos conhecidos...")
        
        try:
            self.tree_builder = FuzzyTreeBuilder(dishes_csv)
            tree, learned_rules = self.tree_builder.train(max_depth=4)
            self.learned_rules = learned_rules
            
            # Converter regras aprendidas para regras fuzzy do scikit-fuzzy
            self.rules = self._convert_learned_rules_to_fuzzy()
            
            logger.info(f"{len(self.rules)} regras geradas automaticamente")
        except Exception as e:
            logger.error(f"Erro ao aprender regras: {e}. Usando regras padrão.")
            self._use_default_rules()
    
    def _convert_learned_rules_to_fuzzy(self) -> List:
        """Converte regras aprendidas para formato scikit-fuzzy"""
        fuzzy_rules = []
        
        # Mapear atributos para variáveis fuzzy
        attr_map = {
            'intensidade_sabor': self.intensidade_sabor,
            'acidez': self.acidez,
            'gordura': self.gordura,
            'especiarias': self.especiarias,
            'dulcor': self.dulcor,
            'proteina': self.proteina,
            'metodo_preparo': self.metodo_preparo
        }
        
        # SEMPRE adicionar regras padrão primeiro para garantir que todos os antecedentes sejam usados
        fuzzy_rules.extend(self._get_default_rules())
        logger.info(f"Adicionadas {len(fuzzy_rules)} regras padrão")
        
        # Tentar adicionar regras aprendidas (mas não é crítico se falhar)
        for rule in self.learned_rules:
            try:
                # Construir antecedentes
                antecedents = []
                for attr, (fuzzy_val, _) in rule.conditions.items():
                    if attr in attr_map:
                        antecedents.append(attr_map[attr][fuzzy_val])
                
                if not antecedents:
                    continue
                
                # Combinar antecedentes com AND
                combined = antecedents[0]
                for ant in antecedents[1:]:
                    combined = combined & ant
                
                # Criar regra
                fuzzy_rule = ctrl.Rule(combined, self.perfil_vinho[rule.conclusion])
                fuzzy_rules.append(fuzzy_rule)
                
            except Exception as e:
                logger.debug(f"Não foi possível converter regra: {e}")
                continue
        
        return fuzzy_rules
    
    def _use_default_rules(self):
        """Usa regras fuzzy padrão (manuais)"""
        logger.info("Usando regras fuzzy padrão")
        self.rules = self._get_default_rules()
    
    def _get_default_rules(self) -> List:
        """Retorna regras fuzzy padrão"""
        return [
            # Regras para vinhos leves
            ctrl.Rule(
                self.intensidade_sabor['baixo'] & self.gordura['baixa'],
                self.perfil_vinho['leve']
            ),
            ctrl.Rule(
                self.intensidade_sabor['baixo'] & self.acidez['alta'],
                self.perfil_vinho['leve']
            ),
            ctrl.Rule(
                self.gordura['baixa'] & self.acidez['alta'],
                self.perfil_vinho['leve']
            ),
            ctrl.Rule(
                self.acidez['alta'] & self.especiarias['baixo'],
                self.perfil_vinho['leve']
            ),
            
            # Regras para vinhos médios
            ctrl.Rule(
                self.intensidade_sabor['medio'] & self.gordura['media'],
                self.perfil_vinho['medio']
            ),
            ctrl.Rule(
                self.intensidade_sabor['medio'] & self.especiarias['medio'],
                self.perfil_vinho['medio']
            ),
            ctrl.Rule(
                self.acidez['media'] & self.gordura['media'],
                self.perfil_vinho['medio']
            ),
            ctrl.Rule(
                self.intensidade_sabor['medio'] & self.acidez['media'],
                self.perfil_vinho['medio']
            ),
            
            # Regras para vinhos encorpados
            ctrl.Rule(
                self.intensidade_sabor['alto'] & self.gordura['alta'],
                self.perfil_vinho['encorpado']
            ),
            ctrl.Rule(
                self.intensidade_sabor['alto'] & self.especiarias['alto'],
                self.perfil_vinho['encorpado']
            ),
            ctrl.Rule(
                self.gordura['alta'] & self.especiarias['alto'],
                self.perfil_vinho['encorpado']
            ),
            ctrl.Rule(
                self.acidez['baixa'] & self.intensidade_sabor['alto'],
                self.perfil_vinho['encorpado']
            ),
            
            # Regras especiais para pratos doces
            ctrl.Rule(
                self.dulcor['alto'] & self.acidez['baixa'],
                self.perfil_vinho['encorpado']
            ),
            ctrl.Rule(
                self.dulcor['alto'] & self.intensidade_sabor['alto'],
                self.perfil_vinho['encorpado']
            ),
            ctrl.Rule(
                self.dulcor['medio'] & self.acidez['alta'],
                self.perfil_vinho['medio']
            ),
        ]
    
    def compute_wine_profile(self, params: Dict[str, float]) -> Dict[str, any]:
        """
        Calcula o perfil de vinho baseado nos parâmetros do prato.
        Retorna um dict com o valor numérico e a categoria (leve/medio/encorpado).
        """
        logger.info("Calculando perfil fuzzy do vinho")
        
        # Definir apenas os inputs que são realmente necessários
        for input_name in self.required_inputs:
            self.simulator.input[input_name] = params.get(input_name, 5.0)
        
        try:
            self.simulator.compute()
            perfil_valor = self.simulator.output['perfil_vinho']
        except Exception as e:
            logger.warning(f"Erro no cálculo fuzzy: {e}. Usando método alternativo.")
            # Fallback: cálculo simples baseado em intensidade e gordura
            intensidade = params.get('intensidade_sabor', 5.0)
            gordura = params.get('gordura', 5.0)
            dulcor = params.get('dulcor', 5.0)
            
            if dulcor > 7:
                perfil_valor = 8.0  # Sobremesas -> encorpado/doce
            elif intensidade > 7 and gordura > 6:
                perfil_valor = 8.0  # encorpado
            elif intensidade < 5 and gordura < 5:
                perfil_valor = 3.0  # leve
            else:
                perfil_valor = 5.0  # medio
        
        # Categorização
        if perfil_valor < 4:
            categoria = 'leve'
        elif perfil_valor < 7:
            categoria = 'medio'
        else:
            categoria = 'encorpado'
        
        logger.info(f"Perfil calculado: {categoria} ({perfil_valor:.2f})")
        
        return {
            'valor': perfil_valor,
            'categoria': categoria
        }
    
    def get_rules_text(self) -> List[str]:
        """Retorna lista de regras em formato legível"""
        if self.tree_builder and self.learned_rules:
            return self.tree_builder.get_rules_text()
        else:
            # Regras padrão em texto
            return [
                "1. SE intensidade_sabor é baixo E gordura é baixa ENTÃO perfil=leve",
                "2. SE intensidade_sabor é baixo E acidez é alta ENTÃO perfil=leve",
                "3. SE gordura é baixa E acidez é alta ENTÃO perfil=leve",
                "4. SE acidez é alta E especiarias é baixo ENTÃO perfil=leve",
                "5. SE intensidade_sabor é medio E gordura é media ENTÃO perfil=medio",
                "6. SE intensidade_sabor é medio E especiarias é medio ENTÃO perfil=medio",
                "7. SE acidez é media E gordura é media ENTÃO perfil=medio",
                "8. SE intensidade_sabor é medio E acidez é media ENTÃO perfil=medio",
                "9. SE intensidade_sabor é alto E gordura é alta ENTÃO perfil=encorpado",
                "10. SE intensidade_sabor é alto E especiarias é alto ENTÃO perfil=encorpado",
                "11. SE gordura é alta E especiarias é alto ENTÃO perfil=encorpado",
                "12. SE acidez é baixa E intensidade_sabor é alto ENTÃO perfil=encorpado",
                "13. SE dulcor é alto E acidez é baixa ENTÃO perfil=encorpado",
                "14. SE dulcor é alto E intensidade_sabor é alto ENTÃO perfil=encorpado",
                "15. SE dulcor é medio E acidez é alta ENTÃO perfil=medio"
            ]
    
    def get_tree_visualization(self) -> str:
        """Retorna visualização da árvore de decisão"""
        if self.tree_builder:
            return self.tree_builder.get_tree_visualization()
        else:
            return "Árvore de decisão não disponível (usando regras padrão)"
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do modelo"""
        if self.tree_builder:
            return self.tree_builder.get_statistics()
        else:
            return {
                'total_regras': len(self.rules),
                'tipo': 'regras_padrao'
            }
