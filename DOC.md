# 📖 Documentação Técnica - Sistema de Recomendação de Vinhos com IA

## 🎯 Visão Geral do Sistema - Versão 2.0

Este projeto implementa um **sistema híbrido de recomendação de vinhos** que combina:
- **Machine Learning** (Árvore de Decisão) para aprendizado de regras
- **Processamento de Linguagem Natural (LLM)** via Google Gemini
- **Lógica Fuzzy** para inferência de perfis com regras aprendidas
- **Algoritmo de Distância Euclidiana** para matching de vinhos

O sistema recebe descrições textuais de pratos e retorna recomendações precisas de vinhos com justificativas técnicas e sensoriais.

### 🆕 Novidades da Versão 2.0

1. **Aprendizado Automático de Regras**: Sistema aprende com 98 pratos conhecidos
2. **Árvore de Decisão Fuzzy**: Construída usando algoritmo de Gini Impurity
3. **Visualização Interativa**: CLI permite ver regras, árvore e estatísticas
4. **Base Expandida**: 98 pratos e 138 vinhos de diversas regiões
5. **Sistema de Cache**: Otimização de chamadas LLM

---

## 🏗️ Arquitetura do Sistema - Versão 2.0

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DE PROCESSAMENTO V2.0               │
└─────────────────────────────────────────────────────────────┘

Base de Conhecimento (pratos.csv - 98 pratos)
           ↓
┌──────────────────────────┐
│  0. FUZZY TREE BUILDER   │  ← Machine Learning
│  (fuzzy_tree_builder.py) │  ← Gini Impurity Algorithm
└──────────────────────────┘
           ↓
    Árvore de Decisão (profundidade 4)
    + 6 Regras Fuzzy Aprendidas
           ↓
┌─────────────────────────────────────────────────────────────┐
│                    FASE DE RECOMENDAÇÃO                      │
└─────────────────────────────────────────────────────────────┘

Input: "Salmão grelhado com limão"
           ↓
┌──────────────────────────┐
│  1. LLM PROCESSOR        │  ← Gemini 2.0 Flash
│  (llm_processor.py)      │  ← Cache LLM
└──────────────────────────┘
           ↓
    JSON com 10 parâmetros
    {proteina: 8, acidez: 7...}
           ↓
┌──────────────────────────┐
│  2. FUZZY ENGINE         │  ← scikit-fuzzy
│  (fuzzy_engine.py)       │  ← 21 regras (15+6)
└──────────────────────────┘
           ↓
    Perfil: {categoria: "leve", valor: 3.2}
           ↓
┌──────────────────────────┐
│  3. RECOMMENDER          │  ← Pandas + NumPy
│  (recommender.py)        │  ← 138 vinhos
└──────────────────────────┘
           ↓
┌──────────────────────────┐
│  4. LLM JUSTIFICATION    │  ← Gemini 2.0 Flash
│  (recommender.py)        │  ← 3 parágrafos
└──────────────────────────┘
           ↓
Output: Vinho + Justificativa Detalhada
```

---

## 🌳 Componente 0: Fuzzy Tree Builder (NOVO!)

### Objetivo
Aprender automaticamente regras fuzzy a partir de uma base de pratos conhecidos, eliminando a necessidade de definição manual de todas as regras.

### Algoritmo de Machine Learning

#### Árvore de Decisão
Utiliza o critério de **Gini Impurity** para construir uma árvore de decisão:

```python
class FuzzyTreeBuilder:
    def calculate_gini_impurity(samples):
        gini = 1.0
        for categoria in ['leve', 'medio', 'encorpado']:
            p = count(categoria) / total
            gini -= p²
        return gini
```

#### Processo de Treinamento

1. **Carregamento de Dados**
   ```python
   pratos.csv → 98 pratos com parâmetros
   ```

2. **Mapeamento de Harmonizações**
   ```
   "branco leve" → leve
   "tinto encorpado" → encorpado
   "tinto médio" → medio
   ```

3. **Construção da Árvore (Recursivo)**
   ```python
   def build_tree(samples, depth=0, max_depth=4):
       # Critério de parada
       if puro(samples) or depth >= max_depth:
           return Leaf(categoria_majoritaria)
       
       # Encontrar melhor split
       best_attr, best_threshold = find_best_split(samples)
       
       # Dividir e recursão
       left = samples[attr <= threshold]
       right = samples[attr > threshold]
       return Node(best_attr, best_threshold, 
                   build_tree(left), build_tree(right))
   ```

4. **Extração de Regras**
   ```python
   def extract_rules(node, conditions=[]):
       if is_leaf(node):
           # Criar regra fuzzy
           rule = create_rule(conditions, node.categoria)
           rules.append(rule)
       else:
           # Explorar ramos
           extract_rules(node.left, [..., attr<=threshold])
           extract_rules(node.right, [..., attr>threshold])
   ```

5. **Fuzzificação de Thresholds**
   ```python
   def fuzzify_value(attr, value):
       if value < 4:  return 'baixo'
       elif value < 7: return 'medio'
       else: return 'alto'
   ```

### Exemplo de Árvore Gerada

```
├─ intensidade_sabor <= 8.50
│  ├─ acidez <= 6.50
│  │  ├─ especiarias <= 2.50
│  │  │  ├─ acidez <= 5.00
│  │  │  │  └─ LEAF: ENCORPADO (9 pratos, conf: 0.78)
│  │  │  └─ acidez > 5.00
│  │  │     └─ LEAF: LEVE (2 pratos, conf: 1.00)
│  │  └─ especiarias > 2.50
│  │     ├─ metodo_preparo <= 4.50
│  │     │  └─ LEAF: LEVE (4 pratos, conf: 1.00)
│  │     └─ metodo_preparo > 4.50
│  │        └─ LEAF: MEDIO (61 pratos, conf: 0.80)
│  └─ acidez > 6.50
│     └─ LEAF: LEVE (7 pratos, conf: 1.00)
└─ intensidade_sabor > 8.50
   └─ LEAF: ENCORPADO (15 pratos, conf: 1.00)
```

### Regras Fuzzy Geradas

```
1. SE intensidade_sabor é alto ENTÃO perfil=encorpado
   [Confiança: 1.00, Suporte: 15 pratos]

2. SE intensidade_sabor é alto E acidez é media ENTÃO perfil=leve
   [Confiança: 1.00, Suporte: 7 pratos]

3. SE intensidade_sabor é alto E acidez é media E 
   especiarias é baixo E metodo_preparo é medio 
   ENTÃO perfil=medio
   [Confiança: 0.80, Suporte: 61 pratos]
```

### Métricas do Modelo

| Métrica | Valor |
|---------|-------|
| Total de pratos | 98 |
| Regras aprendidas | 6 |
| Profundidade máxima | 4 níveis |
| Acurácia estimada | ~80% |
| Tempo de treinamento | <1 segundo |

### Feature Importance

Atributos mais importantes para decisão:

1. **acidez**: 0.2981 (29.8%)
2. **intensidade_sabor**: 0.1468 (14.7%)
3. **especiarias**: 0.0928 (9.3%)
4. **metodo_preparo**: 0.0848 (8.5%)

---

## 🧠 Componente 1: LLM Processor

### Objetivo
Transformar descrições textuais não estruturadas em vetores de características numéricas.

### Modelo Utilizado
- **Google Gemini 2.0 Flash** (`gemini-2.0-flash`)
- Escolhido por: velocidade, acurácia e suporte a JSON estruturado

### Algoritmo de Extração

```python
class LLMProcessor:
    def analyze_dish(dish_description: str) -> dict
```

**Processo:**
1. **Prompt Engineering**: Instrui a LLM a retornar JSON com 10 parâmetros específicos
2. **Parsing Robusto**: Remove markdown code blocks (```json```)
3. **Validação**: Garante que todos os parâmetros estejam entre 0-10
4. **Normalização**: Força valores extremos para limites válidos

### Parâmetros Extraídos

| Parâmetro | Escala | Descrição |
|-----------|--------|-----------|
| `proteina` | 0-10 | Quantidade de proteína no prato |
| `gordura` | 0-10 | Nível de gordura/oleosidade |
| `acidez` | 0-10 | Acidez dos ingredientes principais |
| `dulcor` | 0-10 | Doçura do prato |
| `intensidade_sabor` | 0-10 | Intensidade geral dos sabores |
| `crocancia` | 0-10 | Presença de texturas crocantes |
| `metodo_preparo` | 0-10 | 0=cru, 5=cozido, 10=defumado |
| `especiarias` | 0-10 | Presença de temperos e especiarias |
| `teor_umami` | 0-10 | Nível de umami (glutamato) |
| `nivel_salgado` | 0-10 | Salinidade do prato |

### Tratamento de Erros
```python
try:
    params = json.loads(text)
except json.JSONDecodeError:
    raise ValueError("Erro ao parsear JSON")
```

### Sistema de Cache LLM (NOVO!)

O `LLMProcessor` inclui cache automático para otimizar:

```python
class LLMCache:
    def __init__(self, cache_file='.cache/llm_cache.json'):
        self.cache = self._load_cache()
    
    def get(self, dish_description):
        hash_key = md5(dish_description)
        return self.cache.get(hash_key)
    
    def set(self, dish_description, params):
        hash_key = md5(dish_description)
        self.cache[hash_key] = params
        self._save_cache()
```

**Benefícios:**
- Reduz custo de API calls
- Melhora tempo de resposta (2-3s → <0.1s)
- Permite uso offline para pratos já analisados

---

## 🔀 Componente 2: Fuzzy Engine (Atualizado com ML)

### Objetivo
Calcular o **perfil de vinho ideal** usando lógica fuzzy HÍBRIDA:
- **Regras aprendidas** da árvore de decisão (ML)
- **Regras padrão** para garantir robustez (fallback)

### Framework Utilizado
- **scikit-fuzzy** (versão controle)
- Implementa sistema Mamdani de inferência fuzzy

### Arquitetura Fuzzy Híbrida

#### Modo de Operação Dual

```python
class FuzzyEngine:
    def __init__(self, dishes_csv=None, use_learned_rules=True):
        if use_learned_rules and dishes_csv:
            # Modo ML: Aprender regras
            self.tree_builder = FuzzyTreeBuilder(dishes_csv)
            tree, learned_rules = self.tree_builder.train()
            
            # Combinar: padrão (15) + aprendidas (6)
            self.rules = default_rules + learned_rules
        else:
            # Modo Manual: Apenas regras padrão
            self.rules = default_rules
```

#### Sistema de Detecção Automática de Inputs

**NOVO!** O sistema detecta dinamicamente quais antecedentes são necessários:

```python
def _detect_required_inputs(self):
    self.required_inputs = {'intensidade_sabor', 'acidez', 
                           'gordura', 'especiarias', 'dulcor'}
    
    # Detectar se regras usam proteina ou metodo_preparo
    for rule in self.rules:
        if 'proteina' in str(rule):
            self.required_inputs.add('proteina')
        if 'metodo_preparo' in str(rule):
            self.required_inputs.add('metodo_preparo')
```

Isso evita erros "Unexpected input" ao processar pratos.

#### Variáveis de Entrada (Antecedentes)

```python
# 7 variáveis fuzzy (5 sempre ativas + 2 opcionais)
intensidade_sabor = [0, 10]  # sempre ativa
acidez = [0, 10]             # sempre ativa
gordura = [0, 10]            # sempre ativa
especiarias = [0, 10]        # sempre ativa
dulcor = [0, 10]             # sempre ativa
proteina = [0, 10]           # ativa se usada em regras
metodo_preparo = [0, 10]     # ativa se usada em regras
```

#### Funções de Pertinência (Membership Functions)
Utiliza **funções triangulares (trimf)** para modelar conjuntos fuzzy:

```python
# Exemplo para intensidade_sabor
baixo = trimf([0, 0, 5])    # pico em 0, base em [0,5]
medio = trimf([3, 5, 7])    # pico em 5, base em [3,7]
alto = trimf([5, 10, 10])   # pico em 10, base em [5,10]
```

**Visualização:**
```
     baixo        medio        alto
       /\          /\          /\
      /  \        /  \        /  \
     /    \      /    \      /    \
    /______\____/______\____/______\
    0   3   5   7   10
```

#### Base de Regras Fuzzy Híbrida (21 regras)

**15 Regras Padrão (Manuais)** - Garantem cobertura completa:

1. `SE intensidade_sabor=baixo E gordura=baixa → perfil=leve`
2. `SE intensidade_sabor=baixo E acidez=alta → perfil=leve`
3. `SE gordura=baixa E acidez=alta → perfil=leve`
4. `SE acidez=alta E especiarias=baixo → perfil=leve`
5. `SE intensidade_sabor=medio E gordura=media → perfil=medio`
6. `SE intensidade_sabor=medio E especiarias=medio → perfil=medio`
7. `SE acidez=media E gordura=media → perfil=medio`
8. `SE intensidade_sabor=medio E acidez=media → perfil=medio`
9. `SE intensidade_sabor=alto E gordura=alta → perfil=encorpado`
10. `SE intensidade_sabor=alto E especiarias=alto → perfil=encorpado`
11. `SE gordura=alta E especiarias=alto → perfil=encorpado`
12. `SE acidez=baixa E intensidade_sabor=alto → perfil=encorpado`
13. `SE dulcor=alto E acidez=baixa → perfil=encorpado`
14. `SE dulcor=alto E intensidade_sabor=alto → perfil=encorpado`
15. `SE dulcor=medio E acidez=alta → perfil=medio`

**6 Regras Aprendidas (Machine Learning)** - Especializadas:

16-21. Regras extraídas da árvore de decisão, variando conforme os pratos cadastrados

**Vantagem do Sistema Híbrido:**
- Regras padrão garantem funcionamento mesmo com poucos dados
- Regras aprendidas capturam padrões específicos da base de pratos
- Sistema robusto com fallback automático

### Processo de Inferência

1. **Fuzzificação**: Converte entradas crisp em graus de pertinência
   ```
   Entrada: intensidade_sabor = 6
   Resultado: baixo=0.0, medio=0.5, alto=0.5
   ```

2. **Inferência**: Aplica regras usando operadores AND (mínimo)
   ```python
   Rule: intensidade[medio] AND gordura[media]
   Ativação: min(0.5, 0.6) = 0.5
   ```

3. **Agregação**: Combina todas as regras ativadas (máximo)

4. **Defuzzificação**: Método do centroide para saída crisp
   ```python
   perfil_vinho.defuzzify() → valor numérico [0-10]
   ```

### Categorização Final
```python
if perfil_valor < 4:
    categoria = 'leve'      # vinhos brancos leves, rosés
elif perfil_valor < 7:
    categoria = 'medio'     # tintos médios, brancos encorpados
else:
    categoria = 'encorpado' # tintos potentes, fortificados
```

---

## 🎯 Componente 3: Wine Recommender

### Objetivo
Buscar na base de dados o vinho mais compatível usando cálculo de distância vetorial.

### Base de Dados
- **Formato**: CSV com 100+ vinhos
- **Atributos**: nome, uva, tipo, país, região, acidez, corpo, doçura, intensidade_sabor, harmonizações

### Algoritmo de Recomendação

#### Etapa 1: Filtragem por Perfil Fuzzy
```python
if categoria == 'leve':
    candidatos = vinhos[corpo entre 0-5]
elif categoria == 'medio':
    candidatos = vinhos[corpo entre 4-7]
else:  # encorpado
    candidatos = vinhos[corpo entre 6-10]
```

#### Etapa 2: Cálculo de Distância Euclidiana Ponderada
```python
for vinho in candidatos:
    dist_acidez = |vinho.acidez - prato.acidez|
    dist_intensidade = |vinho.intensidade - prato.intensidade|
    dist_dulcor = |vinho.doçura - prato.dulcor|
    
    score = dist_acidez + dist_intensidade + (0.5 * dist_dulcor)
    # dulcor tem peso menor (0.5) pois é menos crítico
```

**Fórmula Matemática:**
```
Score = √[(va - pa)² + (vi - pi)² + 0.5·(vd - pd)²]
```
Onde:
- `va`, `vi`, `vd` = acidez, intensidade, dulçor do vinho
- `pa`, `pi`, `pd` = acidez, intensidade, dulçor do prato

#### Etapa 3: Seleção do Melhor Match
```python
vinhos_ordenados = sorted(candidatos, key=lambda x: x.score)
vinho_recomendado = vinhos_ordenados[0]  # menor distância
```

---

## 💬 Componente 4: Justificativa via LLM

### Objetivo
Gerar explicação humanizada e técnica da harmonização usando IA.

### Estrutura da Justificativa

O sistema solicita ao Gemini uma resposta em **3 parágrafos**:

#### Parágrafo 1: Harmonização Técnica
- Análise científica de acidez, corpo, taninos
- Comparação numérica dos atributos
- Princípios enológicos aplicados

#### Parágrafo 2: Experiência Sensorial
- Descrição dos sabores no paladar
- Quais características são realçadas
- Equilíbrio de texturas e aromas

#### Parágrafo 3: Fato Interessante
- Curiosidades sobre a uva ou região
- História da vinícola
- Tradições de harmonização

### Prompt Engineering
```python
prompt = f"""
Você é um sommelier expert. Explique por que {vinho} 
harmoniza com o prato (parâmetros: {dish_params}).

Estrutura obrigatória:
1. Harmonização Técnica (2-3 frases)
2. Experiência Sensorial (2-3 frases)
3. Fato Interessante (2-3 frases)

Sem markdown. Linguagem de sommelier profissional.
"""
```

### Fallback
Se a API falhar, o sistema usa justificativa baseada em regras:
```python
def _generate_justification(wine, dish_params):
    # Lógica if-else para criar texto básico
    return justificativa_simples
```

---

## 🔄 Fluxo Completo de Execução

### Entrada do Usuário
```bash
python src/cli.py
🍽️ Prato: Salmão grelhado com molho de limão e aspargos
```

### Processamento Passo a Passo

**1. Análise LLM (2-3s)**
```json
{
  "proteina": 8,
  "gordura": 6,
  "acidez": 7,
  "dulcor": 2,
  "intensidade_sabor": 6,
  "especiarias": 3,
  "metodo_preparo": 8,
  "teor_umami": 5,
  "nivel_salgado": 5
}
```

**2. Cálculo Fuzzy (<1s)**
```
Entradas: intensidade=6, acidez=7, gordura=6, especiarias=3
Fuzzificação → Inferência → Defuzzificação
Resultado: {categoria: "medio", valor: 5.2}
```

**3. Busca no CSV (<1s)**
```
Filtro: vinhos com corpo entre 4-7
Candidatos: 42 vinhos
Cálculo de distâncias...
Melhor match: Chardonnay Chablis (score: 2.1)
```

**4. Justificativa LLM (2-3s)**
```
Parágrafo técnico sobre acidez e frescor...
Parágrafo sensorial sobre limão e manteiga...
Curiosidade sobre a região de Chablis...
```

### Saída Formatada
```
🍾 VINHO RECOMENDADO:
Nome: Chardonnay Chablis Premier Cru
Uva: Chardonnay
Região: Chablis, França
Acidez: 8/10 | Corpo: 5/10 | Doçura: 1/10

💡 POR QUE ESSA HARMONIZAÇÃO?
[3 parágrafos detalhados]
```

---

## 📊 Complexidade Computacional - Versão 2.0

| Componente | Complexidade | Tempo Médio |
|------------|--------------|-------------|
| **Tree Training** | O(n·m·log n) | <1s (uma vez) |
| Rule Extraction | O(k) | <0.1s (uma vez) |
| **LLM Analysis** | O(1)* | 2-3s |
| **Fuzzy Inference** | O(n·r) | <100ms |
| **Wine Matching** | O(m·k) | <500ms |
| **LLM Justification** | O(1)* | 2-3s |

*O(1) para APIs externas (tempo constante de rede)

Onde:
- `n` = número de pratos na base (98)
- `m` = número de vinhos candidatos (~40 após filtro)
- `k` = número de atributos comparados (3)
- `r` = número de regras fuzzy (21 = 15 + 6)

### Otimizações Implementadas

1. **Treinamento único**: Árvore é construída na inicialização
2. **Operações vetorizadas**: Pandas em vez de loops Python
3. **Cache de LLM**: Evita chamadas repetidas à API
4. **Detecção dinâmica de inputs**: Evita processamento desnecessário

**Tempo Total:** ~5-7 segundos (com cache: ~1-3 segundos)

---

## 🧪 Interface CLI Interativa (NOVO!)

### Menu Principal

```
📋 MENU PRINCIPAL
  [1] 🍽️  Recomendar vinho para um prato
  [2] 📊 Visualizar regras fuzzy geradas  
  [3] 🌳 Visualizar árvore de decisão
  [4] 📈 Estatísticas do modelo
  [5] ❌ Sair
```

### Opção 2: Visualizar Regras

Exibe todas as 21 regras fuzzy (15 padrão + 6 aprendidas):

```
1. SE intensidade_sabor é alto ENTÃO perfil=encorpado
   Confiança: 1.00, Suporte: 15 pratos
   
2. SE intensidade_sabor é alto E acidez é media ENTÃO perfil=leve
   Confiança: 1.00, Suporte: 7 pratos
...
```

### Opção 3: Visualizar Árvore

Mostra estrutura hierárquica da árvore de decisão:

```
├─ intensidade_sabor <= 8.50
│  ├─ acidez <= 6.50
│  │  └─ LEAF: MEDIO (61 pratos, conf: 0.80)
│  └─ acidez > 6.50
│     └─ LEAF: LEVE (7 pratos, conf: 1.00)
└─ intensidade_sabor > 8.50
   └─ LEAF: ENCORPADO (15 pratos, conf: 1.00)
```

### Opção 4: Estatísticas

```
Total de pratos analisados: 98
Total de regras geradas: 6
Profundidade da árvore: 4

Distribuição de categorias:
  - medio: 50 pratos
  - encorpado: 28 pratos
  - leve: 20 pratos

Importância dos atributos:
  - acidez: 0.2981
  - intensidade_sabor: 0.1468
  - especiarias: 0.0928
```

---

## 🛠️ Tecnologias e Dependências - Versão 2.0

### Machine Learning & IA
- **google-generativeai 0.3+** - SDK do Gemini 2.0 Flash
- **Algoritmo de Árvore de Decisão** - Gini Impurity (implementação própria)
- **Feature Importance** - Cálculo de relevância de atributos

### Lógica Fuzzy
- **scikit-fuzzy 0.4+** - Motor de lógica fuzzy Mamdani
- **Sistema híbrido** - 15 regras padrão + 6 aprendidas

### Processamento de Dados
- **pandas 2.0+** - Manipulação eficiente de CSV
- **numpy 1.24+** - Operações vetorizadas

### Infraestrutura
- **python-dotenv** - Gestão de variáveis de ambiente
- **Sistema de cache** - Persistência em JSON
- **Sistema de logs** - Rastreabilidade completa

### Instalação Completa
```bash
pip install google-generativeai scikit-fuzzy pandas numpy python-dotenv
```

---

## 🔐 Segurança e Configuração

### Variáveis de Ambiente
```bash
# .env
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.0-flash  # opcional
```

### Boas Práticas
- ✅ `.env` no `.gitignore`
- ✅ `.env.example` versionado (sem chave real)
- ✅ Validação de API key no início
- ✅ Tratamento robusto de exceções
- ✅ Cache com hash MD5 para segurança

### Estrutura de Logs
```
logs/wine_pairing.log
```

Níveis:
- **INFO**: Operações normais
- **WARNING**: Situações que requerem atenção
- **ERROR**: Erros que impedem funcionamento

---

## 📈 Possíveis Melhorias Futuras

### Algoritmos
1. **Random Forest**: Ensemble de múltiplas árvores para maior acurácia
2. **Cross-Validation**: K-fold para validação robusta do modelo
3. **Embeddings Semânticos**: Word2Vec para similaridade de vinhos
4. **Reinforcement Learning**: Aprender com feedback dos usuários
5. **Neural Networks**: Deep Learning para capturar padrões complexos

### Performance
1. **Índices Espaciais**: KD-Tree ou Ball-Tree para busca O(log n)
2. **Cache Distribuído**: Redis para ambiente multi-usuário
3. **Batch Processing**: Processar múltiplos pratos simultaneamente
4. **GPU Acceleration**: CUDA para cálculos matriciais

### Funcionalidades
1. **API REST**: FastAPI com documentação Swagger
2. **Interface Web**: React/Vue.js com visualização interativa
3. **Base Expandida**: 500+ vinhos, 500+ pratos
4. **Multi-idioma**: Suporte a EN, ES, IT, FR
5. **Perfil de Usuário**: Preferências personalizadas
6. **Sistema de Avaliação**: Feedback para melhorar recomendações
7. **Integração com E-commerce**: Compra direta de vinhos
8. **App Mobile**: iOS/Android nativo

### Dados
1. **Web Scraping**: Coletar dados de sites especializados
2. **Crowd-sourcing**: Permitir usuários adicionarem pratos
3. **Expert Review**: Validação por sommeliers profissionais
4. **Rating System**: Avaliações de harmonizações

---

## 🧪 Exemplos de Uso Avançado

### Exemplo 1: Prato Complexo (Alta Intensidade)

```python
# Input
prato = "Costela no bafo com especiarias orientais"

# Processamento
LLM → {intensidade: 9, gordura: 9, especiarias: 8}
Tree → intensidade > 8.5 → ENCORPADO
Fuzzy → aplica regras → valor: 8.7

# Output
Vinho: Syrah Barossa Valley (corpo: 9, intensidade: 9)
Justificativa: "Taninos robustos cortam gordura..."
```

### Exemplo 2: Prato Delicado (Baixa Intensidade)

```python
# Input
prato = "Ceviche de peixe branco com limão"

# Processamento  
LLM → {intensidade: 6, acidez: 8, gordura: 2}
Tree → acidez > 6.5 → LEVE
Fuzzy → aplica regras → valor: 2.8

# Output
Vinho: Albariño Rías Baixas (acidez: 9, corpo: 4)
Justificativa: "Alta acidez complementa limão..."
```

### Exemplo 3: Sobremesa (Alto Dulçor)

```python
# Input
prato = "Torta de chocolate com framboesa"

# Processamento
LLM → {intensidade: 8, dulcor: 9, acidez: 3}
Tree → intensidade > 8.5 → ENCORPADO  
Fuzzy → regra dulçor alto → valor: 8.5

# Output
Vinho: Porto Vintage (doçura: 8, corpo: 10)
Justificativa: "Doçura equilibra chocolate amargo..."
```

---

## 📝 Conclusão - Versão 2.0

Este sistema representa uma **evolução significativa** na fusão de:
- **Machine Learning** (Árvore de Decisão) para aprendizado de padrões
- **IA Generativa** (Gemini) para processamento de linguagem natural
- **Lógica Fuzzy Híbrida** para modelagem de incerteza e robustez
- **Algoritmos clássicos** (distância euclidiana) para matching eficiente

### Diferenciais da Versão 2.0

1. **Aprendizado Automático**: Sistema aprende com dados históricos
2. **Visualização Interativa**: CLI permite explorar o modelo
3. **Sistema Híbrido**: Combina regras manuais com aprendidas
4. **Cache Inteligente**: Otimização de performance
5. **Detecção Dinâmica**: Adaptação automática aos inputs disponíveis

A arquitetura modular permite evolução independente de cada componente, mantendo **alta coesão e baixo acoplamento**.

### Métricas Finais

- ✅ **98 pratos** na base de conhecimento
- ✅ **138 vinhos** de 15+ países
- ✅ **21 regras fuzzy** (híbridas)
- ✅ **~80% acurácia** estimada
- ✅ **<1s tempo de treinamento**
- ✅ **5-7s tempo de recomendação**

**Desenvolvido com 🍷, 🧠, 🤖 e Python**

---

## 📚 Referências Técnicas

### Machine Learning
- Breiman, L. (2001). "Random Forests"
- Quinlan, J.R. (1986). "Induction of Decision Trees"
- Gini, C. (1912). "Variabilità e Mutabilità"

### Lógica Fuzzy
- Zadeh, L.A. (1965). "Fuzzy Sets"
- Mamdani, E.H. (1974). "Application of Fuzzy Logic"
- Klir, G. & Yuan, B. (1995). "Fuzzy Sets and Fuzzy Logic"

### Wine Pairing
- Robinson, J. (2015). "The Oxford Companion to Wine"
- Parr, W. et al. (2007). "Wine-Food Combinations"
- Harrington, R. (2008). "Food and Wine Pairing"

---

**Última Atualização:** Novembro 2025  
**Versão:** 2.0  
**Status:** ✅ Produção
