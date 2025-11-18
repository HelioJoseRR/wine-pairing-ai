#!/usr/bin/env python3
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.llm_processor import LLMProcessor
from src.fuzzy_engine import FuzzyEngine
from src.recommender import WineRecommender

def print_header():
    print("=" * 70)
    print("🍷  SISTEMA INTELIGENTE DE RECOMENDAÇÃO DE VINHOS  🍷")
    print("=" * 70)
    print()

def print_separator():
    print("-" * 70)

def print_dish_params(params):
    print("\n📊 ANÁLISE DO PRATO (via Gemini AI):")
    print_separator()
    print(f"  Proteína:           {params['proteina']:.1f}/10")
    print(f"  Gordura:            {params['gordura']:.1f}/10")
    print(f"  Acidez:             {params['acidez']:.1f}/10")
    print(f"  Dulçor:             {params['dulcor']:.1f}/10")
    print(f"  Intensidade Sabor:  {params['intensidade_sabor']:.1f}/10")
    print(f"  Crocância:          {params['crocancia']:.1f}/10")
    print(f"  Método Preparo:     {params['metodo_preparo']:.1f}/10")
    print(f"  Especiarias:        {params['especiarias']:.1f}/10")
    print(f"  Teor Umami:         {params['teor_umami']:.1f}/10")
    print(f"  Nível Salgado:      {params['nivel_salgado']:.1f}/10")
    print_separator()

def print_fuzzy_profile(perfil):
    print(f"\n🔍 PERFIL FUZZY CALCULADO:")
    print_separator()
    print(f"  Categoria: {perfil['categoria'].upper()}")
    print(f"  Valor:     {perfil['valor']:.2f}/10")
    print_separator()

def print_recommendation(wine):
    print("\n🍾 VINHO RECOMENDADO:")
    print("=" * 70)
    print(f"  Nome:              {wine['nome']}")
    print(f"  Uva:               {wine['uva']}")
    print(f"  Tipo:              {wine['tipo'].capitalize()}")
    print(f"  País:              {wine['país']}")
    print(f"  Região:            {wine['região']}")
    print(f"  Teor Alcoólico:    {wine['teor_alcoolico']}%")
    print_separator()
    print(f"  Acidez:            {wine['acidez']}/10")
    print(f"  Corpo:             {wine['corpo']}/10")
    print(f"  Doçura:            {wine['doçura']}/10")
    print(f"  Intensidade Sabor: {wine['intensidade_sabor']}/10")
    print_separator()
    print(f"\n💡 POR QUE ESSA HARMONIZAÇÃO?")
    print_separator()
    
    # Formatar justificativa com quebras de linha adequadas
    justificativa = wine['justificativa']
    paragraphs = justificativa.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():
            # Quebrar linhas longas em 70 caracteres
            words = paragraph.strip().split()
            line = "  "
            for word in words:
                if len(line) + len(word) + 1 <= 72:
                    line += word + " "
                else:
                    print(line.rstrip())
                    line = "  " + word + " "
            print(line.rstrip())
            
            # Adicionar espaço entre parágrafos (exceto no último)
            if i < len(paragraphs) - 1:
                print()
    
    print_separator()
    print(f"\n🍽️  OUTRAS HARMONIZAÇÕES:")
    print(f"  {wine['harmonizacoes']}")
    print("=" * 70)

def main():
    print_header()
    
    # Paths
    csv_path = root_dir / "data" / "vinhos.csv"
    
    try:
        # Solicitar descrição do prato
        print("Por favor, descreva o prato para o qual deseja uma recomendação de vinho:")
        print("(Ex: 'Filé mignon grelhado com molho de cogumelos')")
        print()
        dish_description = input("🍽️  Prato: ").strip()
        
        if not dish_description:
            print("❌ Descrição do prato não pode estar vazia.")
            return
        
        print("\n⏳ Processando com Gemini AI...")
        
        # 1. Processar com LLM
        llm = LLMProcessor()
        dish_params = llm.analyze_dish(dish_description)
        
        print_dish_params(dish_params)
        
        # 2. Calcular perfil fuzzy
        print("\n⏳ Calculando perfil fuzzy...")
        fuzzy = FuzzyEngine()
        perfil_fuzzy = fuzzy.compute_wine_profile(dish_params)
        
        print_fuzzy_profile(perfil_fuzzy)
        
        # 3. Recomendar vinho
        print("\n⏳ Buscando o vinho ideal...")
        recommender = WineRecommender(str(csv_path))
        wine = recommender.recommend(dish_params, perfil_fuzzy)
        
        print_recommendation(wine)
        
        print("\n✅ Recomendação concluída com sucesso!\n")
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {csv_path} não encontrado.")
        print("   Certifique-se de que o arquivo data/vinhos.csv existe.")
    except ValueError as e:
        print(f"❌ Erro: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
