import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyEngine:
    def __init__(self):
        # Variáveis de entrada
        self.intensidade_sabor = ctrl.Antecedent(np.arange(0, 11, 1), 'intensidade_sabor')
        self.acidez = ctrl.Antecedent(np.arange(0, 11, 1), 'acidez')
        self.gordura = ctrl.Antecedent(np.arange(0, 11, 1), 'gordura')
        self.especiarias = ctrl.Antecedent(np.arange(0, 11, 1), 'especiarias')
        
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
        
        # Funções de pertinência para perfil do vinho
        self.perfil_vinho['leve'] = fuzz.trimf(self.perfil_vinho.universe, [0, 0, 5])
        self.perfil_vinho['medio'] = fuzz.trimf(self.perfil_vinho.universe, [3, 5, 7])
        self.perfil_vinho['encorpado'] = fuzz.trimf(self.perfil_vinho.universe, [5, 10, 10])
        
        # Regras fuzzy
        self.rules = [
            ctrl.Rule(
                self.intensidade_sabor['baixo'] & self.gordura['baixa'],
                self.perfil_vinho['leve']
            ),
            ctrl.Rule(
                self.intensidade_sabor['baixo'] & self.acidez['alta'],
                self.perfil_vinho['leve']
            ),
            ctrl.Rule(
                self.intensidade_sabor['medio'] & self.gordura['media'],
                self.perfil_vinho['medio']
            ),
            ctrl.Rule(
                self.intensidade_sabor['medio'] & self.especiarias['medio'],
                self.perfil_vinho['medio']
            ),
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
                self.gordura['baixa'] & self.acidez['alta'],
                self.perfil_vinho['leve']
            ),
            ctrl.Rule(
                self.acidez['baixa'] & self.intensidade_sabor['alto'],
                self.perfil_vinho['encorpado']
            ),
        ]
        
        # Sistema de controle
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)
    
    def compute_wine_profile(self, params: dict) -> dict:
        """
        Calcula o perfil de vinho baseado nos parâmetros do prato.
        Retorna um dict com o valor numérico e a categoria (leve/medio/encorpado).
        """
        self.simulator.input['intensidade_sabor'] = params['intensidade_sabor']
        self.simulator.input['acidez'] = params['acidez']
        self.simulator.input['gordura'] = params['gordura']
        self.simulator.input['especiarias'] = params['especiarias']
        
        self.simulator.compute()
        
        perfil_valor = self.simulator.output['perfil_vinho']
        
        # Categorização
        if perfil_valor < 4:
            categoria = 'leve'
        elif perfil_valor < 7:
            categoria = 'medio'
        else:
            categoria = 'encorpado'
        
        return {
            'valor': perfil_valor,
            'categoria': categoria
        }
