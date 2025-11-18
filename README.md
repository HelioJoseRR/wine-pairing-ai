# 🍷 Sistema Inteligente de Recomendação de Vinhos

Sistema avançado de recomendação de vinhos que combina **Lógica Fuzzy** e **Inteligência Artificial (LLM)** para sugerir o vinho perfeito para qualquer prato.

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

Este sistema utiliza três componentes principais:

1. **LLM (Gemini AI)**: Analisa a descrição textual do prato e extrai 10 parâmetros estruturados
2. **Lógica Fuzzy**: Processa os parâmetros e determina o perfil ideal de vinho (leve, médio, encorpado)
3. **Recomendador**: Busca na base de dados (100+ vinhos) e seleciona o vinho mais compatível
4. **✨ Justificativa Inteligente**: Gemini gera explicação detalhada com harmonização técnica, experiência sensorial e fatos interessantes sobre o vinho

## 🏗️ Arquitetura

```
Descrição do Prato (texto livre)
         ↓
    [Gemini AI] → Extração de 10 parâmetros estruturados
         ↓
  [Fuzzy Engine] → Cálculo do perfil de vinho
         ↓
  [Recommender] → Busca no CSV e seleção
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

O sistema solicitará a descrição de um prato. Exemplo:

```
Por favor, descreva o prato para o qual deseja uma recomendação de vinho:
🍽️  Prato: Salmão grelhado com molho de limão e aspargos
```

Aguarde o processamento (5-10 segundos) e receba:
- Análise completa dos parâmetros do prato (via Gemini)
- Perfil fuzzy calculado (leve/médio/encorpado)
- Recomendação de vinho da base de dados
- **✨ Justificativa expandida** com 3 parágrafos:
  - 🔬 Harmonização técnica (acidez, corpo, taninos)
  - 👅 Experiência sensorial (sabores no paladar)
  - 💡 Fato interessante (história, região, curiosidades)

## 🧠 Como Funciona

### 1. Processamento via LLM (llm_processor.py)

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

### 2. Lógica Fuzzy (fuzzy_engine.py)

O `FuzzyEngine` utiliza scikit-fuzzy para implementar um sistema de inferência fuzzy com:

**Variáveis de Entrada:**
- intensidade_sabor (baixo, médio, alto)
- acidez (baixa, média, alta)
- gordura (baixa, média, alta)
- especiarias (baixo, médio, alto)

**Variável de Saída:**
- perfil_vinho (leve, médio, encorpado)

**Regras Fuzzy (exemplos):**
- SE intensidade_sabor é baixo E gordura é baixa → ENTÃO perfil é leve
- SE intensidade_sabor é alto E gordura é alta → ENTÃO perfil é encorpado
- SE gordura é alta E especiarias é alto → ENTÃO perfil é encorpado

O sistema aplica as regras e retorna um valor numérico (0-10) que é categorizado.

### 3. Recomendação (recommender.py)

O `WineRecommender`:

1. Filtra vinhos do CSV com base no perfil fuzzy (corpo do vinho)
2. Calcula distância euclidiana entre atributos do prato e de cada vinho candidato
3. Seleciona o vinho com menor distância (melhor match)
4. Gera justificativa textual explicando a escolha

### 4. Base de Dados (vinhos.csv)

O arquivo `data/vinhos.csv` contém 100+ vinhos reais com informações completas:
- Nome, uva, tipo, país, região
- Teor alcoólico
- Atributos sensoriais (acidez, corpo, doçura, intensidade)
- Harmonizações tradicionais

## 📁 Estrutura do Projeto

```
wine-pairing-ai/
│
├── data/
│   └── vinhos.csv              # Base de dados com 100+ vinhos
│
├── src/
│   ├── llm_processor.py        # Integração com Gemini AI
│   ├── fuzzy_engine.py         # Motor de lógica fuzzy
│   ├── recommender.py          # Sistema de recomendação
│   └── cli.py                  # Interface de linha de comando
│
├── .env.example                # Exemplo de configuração
├── .env                        # Suas credenciais (não versionar!)
└── README.md                   # Este arquivo
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

- **Python 3.8+**: Linguagem principal
- **Google Gemini AI**: LLM para análise de linguagem natural
- **scikit-fuzzy**: Implementação de lógica fuzzy
- **pandas**: Manipulação da base de dados CSV
- **numpy**: Operações numéricas
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 🔒 Segurança

- **Nunca** compartilhe sua chave da API Gemini
- O arquivo `.env` deve estar no `.gitignore`
- Use `.env.example` como referência sem dados sensíveis

## 🐛 Troubleshooting

### Erro: "GEMINI_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Confirme que a chave está no formato correto: `GEMINI_API_KEY=sua_chave`

### Erro ao parsear JSON da LLM
- A API do Gemini pode ocasionalmente retornar formatos inesperados
- Execute novamente - o sistema possui tratamento de erros

### Vinhos não encontrados
- Verifique se `data/vinhos.csv` existe
- Confirme que o arquivo tem as colunas corretas

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
