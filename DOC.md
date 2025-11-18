# 📖 Documentação Técnica - Sistema de Recomendação de Vinhos com IA

## 🎯 Visão Geral do Sistema

Este projeto implementa um **sistema híbrido de recomendação de vinhos** que combina:
- **Processamento de Linguagem Natural (LLM)** via Google Gemini
- **Lógica Fuzzy** para inferência de perfis
- **Algoritmo de Distância Euclidiana** para matching de vinhos

O sistema recebe descrições textuais de pratos e retorna recomendações precisas de vinhos com justificativas técnicas e sensoriais.

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DE PROCESSAMENTO                    │
└─────────────────────────────────────────────────────────────┘

Input: "Salmão grelhado com limão"
           ↓
┌──────────────────────────┐
│  1. LLM PROCESSOR        │  ← Gemini 2.0 Flash
│  (llm_processor.py)      │
└──────────────────────────┘
           ↓
    JSON com 10 parâmetros
    {proteina: 8, acidez: 7...}
           ↓
┌──────────────────────────┐
│  2. FUZZY ENGINE         │  ← scikit-fuzzy
│  (fuzzy_engine.py)       │
└──────────────────────────┘
           ↓
    Perfil: {categoria: "leve", valor: 3.2}
           ↓
┌──────────────────────────┐
│  3. RECOMMENDER          │  ← Pandas + NumPy
│  (recommender.py)        │
└──────────────────────────┘
           ↓
┌──────────────────────────┐
│  4. LLM JUSTIFICATION    │  ← Gemini 2.0 Flash
│  (recommender.py)        │
└──────────────────────────┘
           ↓
Output: Vinho + Justificativa Detalhada
```

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

---

## 🔀 Componente 2: Fuzzy Engine

### Objetivo
Calcular o **perfil de vinho ideal** usando lógica fuzzy para lidar com a incerteza inerente às harmonizações gastronômicas.

### Framework Utilizado
- **scikit-fuzzy** (versão controle)
- Implementa sistema Mamdani de inferência fuzzy

### Arquitetura Fuzzy

#### Variáveis de Entrada (Antecedentes)
```python
intensidade_sabor = [0, 10]  # universo de discurso
acidez = [0, 10]
gordura = [0, 10]
especiarias = [0, 10]
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

#### Base de Regras Fuzzy (9 regras)

1. `SE intensidade_sabor=baixo E gordura=baixa → perfil=leve`
2. `SE intensidade_sabor=baixo E acidez=alta → perfil=leve`
3. `SE intensidade_sabor=medio E gordura=media → perfil=medio`
4. `SE intensidade_sabor=medio E especiarias=medio → perfil=medio`
5. `SE intensidade_sabor=alto E gordura=alta → perfil=encorpado`
6. `SE intensidade_sabor=alto E especiarias=alto → perfil=encorpado`
7. `SE gordura=alta E especiarias=alto → perfil=encorpado`
8. `SE gordura=baixa E acidez=alta → perfil=leve`
9. `SE acidez=baixa E intensidade_sabor=alto → perfil=encorpado`

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

## 📊 Complexidade Computacional

| Componente | Complexidade | Tempo Médio |
|------------|--------------|-------------|
| LLM Analysis | O(1)* | 2-3s |
| Fuzzy Inference | O(n·r) | <100ms |
| Wine Matching | O(m·k) | <500ms |
| LLM Justification | O(1)* | 2-3s |

*O(1) para APIs externas (tempo constante de rede)

Onde:
- `n` = número de variáveis fuzzy (4)
- `r` = número de regras (9)
- `m` = número de vinhos candidatos (~40)
- `k` = número de atributos comparados (3)

**Tempo Total:** ~5-7 segundos

---

## 🛠️ Tecnologias e Dependências

### Core
- **Python 3.8+**
- **google-generativeai 0.3+** - SDK do Gemini
- **scikit-fuzzy 0.4+** - Motor de lógica fuzzy
- **pandas 2.0+** - Manipulação de dados
- **numpy 1.24+** - Operações numéricas

### Configuração
- **python-dotenv** - Gestão de variáveis de ambiente

### Instalação
```bash
pip install google-generativeai scikit-fuzzy pandas numpy python-dotenv
```

---

## 🔐 Segurança e Configuração

### Variáveis de Ambiente
```bash
# .env
GEMINI_API_KEY=AIzaSy...
```

### Boas Práticas
- ✅ `.env` no `.gitignore`
- ✅ `.env.example` versionado (sem chave real)
- ✅ Validação de API key no início
- ✅ Tratamento de exceções para falhas de API

---

## 📈 Possíveis Melhorias

### Algoritmos
1. **Modelo de ML Supervisionado**: Treinar RandomForest com avaliações de sommeliers
2. **Embeddings**: Usar vetores semânticos para vinhos e pratos
3. **Collaborative Filtering**: Incorporar preferências de usuários
4. **Reinforcement Learning**: Aprender com feedback de harmonizações

### Performance
1. **Cache de LLM**: Armazenar análises de pratos comuns
2. **Indexação de Vinhos**: Usar KD-Tree para busca mais rápida
3. **Batch Processing**: Processar múltiplos pratos simultaneamente

### Funcionalidades
1. **API REST**: Expor sistema via FastAPI
2. **Interface Web**: React/Vue.js frontend
3. **Base Expandida**: 1000+ vinhos com reviews
4. **Multi-idioma**: Suporte a inglês, espanhol, italiano

---

## 🧪 Exemplo de Teste

```python
# test_enhanced.py
prato = "Picanha grelhada com chimichurri"

# Resultado esperado:
# - LLM: intensidade=9, gordura=8, especiarias=7
# - Fuzzy: categoria="encorpado", valor=8.5
# - Vinho: Malbec Argentino ou Cabernet Sauvignon
# - Justificativa: Taninos robustos cortam gordura...
```

---

## 📝 Conclusão

Este sistema representa uma **fusão inovadora** de:
- **IA Generativa** (Gemini) para processamento de linguagem natural
- **Lógica Fuzzy** para modelagem de incerteza
- **Algoritmos clássicos** (distância euclidiana) para matching

A arquitetura modular permite evolução independente de cada componente, mantendo alta coesão e baixo acoplamento.

**Desenvolvido com 🍷, 🧠 e Python**
