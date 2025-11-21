# 🍷 Sistema Inteligente de Recomendação de Vinhos com Machine Learning

Sistema avançado de recomendação de vinhos que combina **Lógica Fuzzy com Machine Learning**, **Árvore de Decisão** e **Inteligência Artificial (LLM)** para sugerir o vinho perfeito para qualquer prato.

##**Vídeo de apresentação**: Pode ser acessado neste link:

###https://drive.google.com/file/d/1Sl0i5KemuOlRi28xWjFaoZeN_qqucx1e/view
🆕 **NOVIDADES DA VERSÃO 2.0:**
- 🌳 **Árvore de Decisão Fuzzy** gerada automaticamente a partir de 98+ pratos conhecidos
- 📊 **Regras Fuzzy Aprendidas** por algoritmo de Machine Learning
- 📈 **Visualização de Regras e Árvore** no CLI
- 🍽️ **Base expandida:** 98 pratos e 138+ vinhos
- 📊 **Estatísticas do Modelo** com importância dos atributos

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Como Funciona](#como-funciona)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Exemplos de Uso](#exemplos-de-uso)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)

## 🎯 Visão Geral


Este sistema utiliza cinco componentes principais:

1. **Base de Conhecimento**: 98 pratos cadastrados com parâmetros gastronômicos
2. **Algoritmo de Aprendizado**: Constrói árvore de decisão e gera regras fuzzy automaticamente
3. **LLM (Gemini AI)**: Analisa a descrição textual do prato e extrai 10 parâmetros estruturados
4. **Lógica Fuzzy com ML**: Aplica regras aprendidas para determinar o perfil ideal de vinho (leve, médio, encorpado)
5. **Recomendador**: Busca na base de dados (138+ vinhos) e seleciona o vinho mais compatível
6. **✨ Justificativa Inteligente**: Gemini gera explicação detalhada com harmonização técnica, experiência sensorial e fatos interessantes

## 🏗️ Arquitetura

```
Base de Conhecimento (98 pratos)
         ↓
  [Fuzzy Tree Builder] → Árvore de Decisão + Regras Fuzzy Aprendidas
         ↓
Descrição do Prato (texto livre do usuário)
         ↓
    [Gemini AI] → Extração de 10 parâmetros estruturados
         ↓
  [Fuzzy Engine com ML] → Aplicação das regras aprendidas
         ↓
  [Recommender] → Busca no CSV de 138+ vinhos
         ↓
    [Gemini AI] → Justificativa expandida (técnica + sensorial + curiosidades)
         ↓
    Recomendação Final Completa
```

## 🔧 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API do Google Gemini

### Passo a passo

1. **Clone ou baixe o projeto:**

```bash
cd wine-pairing-ai
```

2. **Crie um ambiente virtual (recomendado):**

```bash
python -m venv venv
```

3. **Ative o ambiente virtual:**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instale as dependências:**

```bash
pip install google-generativeai python-dotenv pandas numpy scikit-fuzzy
```

## ⚙️ Configuração

### 1. Obter Chave da API Gemini

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma nova chave de API
3. Copie a chave gerada

### 2. Configurar o arquivo .env

1. Copie o arquivo de exemplo:

```bash
copy .env.example .env
```

2. Edite o arquivo `.env` e insira sua chave:

```
GEMINI_API_KEY=sua_chave_real_aqui
```

⚠️ **IMPORTANTE**: Nunca compartilhe ou commite o arquivo `.env` com sua chave real!

## 🚀 Como Usar

Execute o sistema via linha de comando:

```bash
python src/cli.py
```

O sistema apresentará um menu interativo com 5 opções:

```
📋 MENU PRINCIPAL
  [1] 🍽️  Recomendar vinho para um prato
  [2] 📊 Visualizar regras fuzzy geradas
  [3] 🌳 Visualizar árvore de decisão
  [4] 📈 Estatísticas do modelo
  [5] ❌ Sair
```

### Opção 1: Recomendar Vinho

Descreva seu prato e receba:
- Análise completa dos parâmetros (via Gemini)
- Perfil fuzzy calculado pelas regras aprendidas
- Recomendação de vinho da base de dados
- Justificativa detalhada com 3 parágrafos

### Opção 2: Visualizar Regras

Veja todas as regras fuzzy geradas automaticamente:
```
1. SE intensidade_sabor é alto ENTÃO perfil=encorpado
   Confiança: 1.00, Suporte: 15 pratos
2. SE intensidade_sabor é alto E acidez é medio ENTÃO perfil=leve
   Confiança: 1.00, Suporte: 7 pratos
...
```

### Opção 3: Visualizar Árvore

Visualize a árvore de decisão construída:
```
├─ intensidade_sabor <= 8.50
  ├─ acidez <= 6.50
    ├─ especiarias <= 2.50
      └─ LEAF: ENCORPADO (samples: 9, conf: 0.78)
...
```

### Opção 4: Estatísticas

Veja estatísticas do modelo de machine learning:
- Total de pratos analisados
- Regras geradas
- Profundidade da árvore
- Distribuição de categorias
- Importância dos atributos

## 🧠 Como Funciona

### 1. Aprendizado Automático de Regras (fuzzy_tree_builder.py)

**NOVIDADE V2.0**: O sistema agora aprende automaticamente a partir dos pratos conhecidos!

- **Base de Conhecimento**: 98 pratos com parâmetros e harmonizações
- **Algoritmo de Árvore de Decisão**: Constrói árvore usando critério de Gini Impurity
- **Extração de Regras**: Converte a árvore em regras fuzzy interpretáveis
- **Fuzzificação**: Converte thresholds numéricos em termos linguísticos (baixo/médio/alto)

**Exemplo de Regra Gerada:**
```
SE intensidade_sabor é alto E acidez é medio E especiarias é baixo 
ENTÃO perfil=encorpado 
(Confiança: 0.78, Suporte: 9 pratos)
```

### 2. Processamento via LLM (llm_processor.py)

O módulo `LLMProcessor` envia a descrição do prato para o Gemini AI com um prompt estruturado que solicita 10 parâmetros:

- **proteina** (0-10): Quantidade de proteína
- **gordura** (0-10): Nível de gordura do prato
- **acidez** (0-10): Acidez dos ingredientes
- **dulcor** (0-10): Doçura do prato
- **intensidade_sabor** (0-10): Intensidade geral
- **crocancia** (0-10): Textura crocante
- **metodo_preparo** (0-10): 0=cru, 5=cozido, 10=grelhado/defumado
- **especiarias** (0-10): Presença de especiarias
- **teor_umami** (0-10): Nível de umami
- **nivel_salgado** (0-10): Salinidade

A LLM retorna um JSON estruturado que é parseado e validado.

### 3. Lógica Fuzzy com Machine Learning (fuzzy_engine.py)

**MUDANÇA IMPORTANTE**: O sistema agora usa regras aprendidas automaticamente!

O `FuzzyEngine` pode operar em dois modos:
1. **Modo com ML (padrão)**: Usa regras extraídas da árvore de decisão
2. **Modo manual (fallback)**: Usa 15 regras pré-definidas

**Processo:**
1. Carrega base de pratos (`pratos.csv`)
2. Treina árvore de decisão (max_depth=4)
3. Extrai regras da árvore
4. Converte regras para formato scikit-fuzzy
5. Aplica regras ao novo prato do usuário

**Variáveis de Entrada:**
- intensidade_sabor, acidez, gordura, especiarias, dulcor, proteina, metodo_preparo

**Variável de Saída:**
- perfil_vinho (leve: 0-4, médio: 4-7, encorpado: 7-10)

**Métricas do Modelo:**
- Profundidade da árvore: 4 níveis
- Regras geradas: 6+ regras
- Atributo mais importante: acidez (0.2981)

### 4. Recomendação (recommender.py)

O `WineRecommender`:

1. Filtra vinhos do CSV com base no perfil fuzzy (corpo do vinho)
2. Calcula distância euclidiana entre atributos do prato e de cada vinho candidato
3. Seleciona o vinho com menor distância (melhor match)
4. Gera justificativa textual explicando a escolha

### 5. Base de Dados

**Vinhos (vinhos.csv)**: 138+ vinhos de diversas regiões
- Tintos, brancos, rosés, espumantes, fortificados
- Países: França, Itália, Espanha, Portugal, Argentina, Chile, EUA, Austrália, etc.
- Atributos: acidez, corpo, doçura, intensidade

**Pratos (pratos.csv)**: 98 pratos cadastrados
- Categorias: Carne Vermelha, Peixe, Frutos do Mar, Massas, Sobremesas, etc.
- 10 parâmetros por prato
- Harmonização sugerida (leve/médio/encorpado)

## 📁 Estrutura do Projeto

```
wine-pairing-ai/
│
├── data/
│   ├── vinhos.csv              # Base de dados com 138+ vinhos
│   └── pratos.csv              # Base de conhecimento com 98 pratos
│
├── src/
│   ├── cache.py                 # Sistema de cache para LLM
│   ├── llm_processor.py         # Integração com Gemini AI
│   ├── fuzzy_tree_builder.py   # 🆕 Construção de árvore e regras ML
│   ├── fuzzy_engine.py          # Motor de lógica fuzzy com ML
│   ├── recommender.py           # Sistema de recomendação
│   ├── dish_database.py         # Gerenciador da base de pratos
│   ├── config.py                # Configurações do sistema
│   ├── logger.py                # Sistema de logs
│   └── cli.py                   # Interface CLI interativa
│
├── logs/                        # Logs de execução
├── .cache/                      # Cache de respostas LLM
│
├── .env.example                 # Exemplo de configuração
├── .env                         # Suas credenciais (não versionar!)
├── DOC.md                       # Documentação técnica detalhada
└── README.md                    # Este arquivo
```

## 💡 Exemplos de Uso

### Exemplo 1: Carne Vermelha

```
🍽️  Prato: Filé mignon ao molho madeira com batatas rústicas

Resultado esperado:
- Perfil: Encorpado
- Vinho: Cabernet Sauvignon ou similar
- Justificativa: Corpo robusto para equilibrar a intensidade da carne
```

### Exemplo 2: Peixe Leve

```
🍽️  Prato: Ceviche de peixe branco com limão e coentro

Resultado esperado:
- Perfil: Leve
- Vinho: Sauvignon Blanc ou Albariño
- Justificativa: Alta acidez harmoniza com o limão e frescor do prato
```

### Exemplo 3: Massa

```
🍽️  Prato: Fettuccine alfredo com frango e cogumelos

Resultado esperado:
- Perfil: Médio
- Vinho: Chardonnay ou Pinot Grigio
- Justificativa: Corpo médio equilibra o cremoso do molho
```

### Exemplo 4: Sobremesa

```
🍽️  Prato: Torta de chocolate com frutas vermelhas

Resultado esperado:
- Perfil: Encorpado/Doce
- Vinho: Porto ou Amarone
- Justificativa: Doçura e intensidade complementam o chocolate
```

## 🛠️ Tecnologias Utilizadas

### Machine Learning & IA
- **Google Gemini AI 2.0 Flash**: LLM para análise de linguagem natural e geração de justificativas
- **Algoritmo de Árvore de Decisão**: Gini Impurity para construção da árvore
- **Aprendizado Automático de Regras**: Extração de regras fuzzy a partir de dados históricos

### Lógica Fuzzy
- **scikit-fuzzy**: Implementação de lógica fuzzy Mamdani
- **Funções de pertinência triangulares**: Modelagem de incerteza
- **Sistema de inferência**: 21 regras (15 padrão + 6 aprendidas)

### Processamento de Dados
- **pandas**: Manipulação de bases de dados CSV
- **numpy**: Operações numéricas e vetoriais

### Infraestrutura
- **Python 3.8+**: Linguagem principal
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **Sistema de cache**: Otimização de chamadas à LLM
- **Sistema de logs**: Monitoramento e debugging

## 📊 Métricas do Sistema

### Base de Conhecimento
- **98 pratos** cadastrados com parâmetros completos
- **138 vinhos** de 15+ países e regiões
- **10 parâmetros** por prato para análise detalhada

### Modelo de Machine Learning
- **Profundidade da árvore**: 4 níveis
- **Regras geradas**: 6 regras principais aprendidas
- **Acurácia estimada**: ~80% (baseado em confidence)
- **Atributo mais relevante**: Acidez (29.8%)
- **Tempo de treinamento**: <1 segundo

### Performance
- **Tempo total de recomendação**: 5-10 segundos
  - LLM análise: 2-3s
  - Fuzzy inference: <0.1s
  - Matching: <0.5s
  - LLM justificativa: 2-3s
- **Cache de LLM**: Reduz tempo em requisições repetidas

## 🔒 Segurança

- **Nunca** compartilhe sua chave da API Gemini
- O arquivo `.env` deve estar no `.gitignore`
- Use `.env.example` como referência sem dados sensíveis

## 🐛 Troubleshooting

### Erro: "GEMINI_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Confirme que a chave está no formato correto: `GEMINI_API_KEY=sua_chave`
- Certifique-se de que não há espaços extras na linha

### Erro ao parsear JSON da LLM
- A API do Gemini pode ocasionalmente retornar formatos inesperados
- Execute novamente - o sistema possui tratamento de erros robusto
- Verifique sua conexão com a internet

### Vinhos não encontrados
- Verifique se `data/vinhos.csv` existe e está completo
- Confirme que o arquivo tem as colunas corretas
- Execute: `python -c "import pandas as pd; print(pd.read_csv('data/vinhos.csv').shape)"`

### Erro "Unexpected input"
- O sistema detecta automaticamente quais inputs são necessários
- Se persistir, tente remover o cache: `.cache/llm_cache.json`

### Menu não aparece
- Certifique-se de estar usando Python 3.8+
- Verifique se todas as dependências estão instaladas: `pip list`
- Tente executar: `python src/cli.py` dentro do ambiente virtual

## 🔍 Funcionalidades Avançadas

### Sistema de Cache
O sistema mantém cache das análises LLM para:
- Reduzir custo de API calls
- Melhorar tempo de resposta
- Permitir uso offline para pratos já analisados

Cache localizado em: `.cache/llm_cache.json`

### Logs Detalhados
Todos os eventos são registrados em: `logs/wine_pairing.log`
- Nível INFO: Operações normais
- Nível WARNING: Situações que requerem atenção
- Nível ERROR: Erros que impedem funcionamento

### Detecção Automática de Inputs
O fuzzy engine detecta automaticamente quais parâmetros são necessários baseado nas regras ativas, evitando erros de configuração.

## 🎓 Conceitos Aplicados

### Machine Learning
- **Árvore de Decisão**: Algoritmo supervisionado para classificação
- **Gini Impurity**: Métrica de qualidade dos splits
- **Feature Importance**: Identificação dos atributos mais relevantes

### Lógica Fuzzy
- **Conjuntos Fuzzy**: Modelagem de incerteza linguística
- **Fuzzificação/Defuzzificação**: Conversão entre valores crisp e fuzzy
- **Inferência Mamdani**: Sistema de regras IF-THEN

### Engenharia de Software
- **Arquitetura Modular**: Separação de responsabilidades
- **Cache Inteligente**: Otimização de performance
- **Logging**: Rastreabilidade e debugging
- **Error Handling**: Tratamento robusto de exceções

## 📝 Licença

Este projeto é fornecido como está para fins educacionais e de demonstração.

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Sinta-se livre para:
- Adicionar mais vinhos ao CSV
- Melhorar as regras fuzzy
- Otimizar o algoritmo de recomendação
- Aprimorar a interface CLI

---

**Desenvolvido com 🍷 e Python**
