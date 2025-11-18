#!/usr/bin/env python3
import sys
import re
from pathlib import Path
from typing import Set

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.llm_processor import LLMProcessor
from src.fuzzy_engine import FuzzyEngine
from src.recommender import WineRecommender
from src.config import MAX_DISH_DESCRIPTION_LENGTH, MIN_DISH_DESCRIPTION_LENGTH
from src.logger import setup_logger

logger = setup_logger(__name__)

def print_header():
    print("=" * 80)
    print("🍷  SISTEMA INTELIGENTE DE RECOMENDAÇÃO DE VINHOS COM IA  🍷")
    print("=" * 80)
    print("     Powered by: Fuzzy Logic + Machine Learning + Gemini AI")
    print("=" * 80)
    print()

def print_separator():
    print("-" * 80)

def get_main_menu_choice() -> str:
    """Menu principal do sistema"""
    print("\n📋 MENU PRINCIPAL")
    print("=" * 80)
    print()
    print("  [1] 🍽️  Recomendar vinho para um prato")
    print("  [2] 📊 Visualizar regras fuzzy geradas")
    print("  [3] 🌳 Visualizar árvore de decisão")
    print("  [4] 📈 Estatísticas do modelo")
    print("  [5] ❌ Sair")
    print()
    print_separator()
    
    choice = input("Escolha uma opção (1-5): ").strip()
    return choice


def get_output_options() -> Set[int]:
    print("\n📋 OPÇÕES DE SAÍDA")
    print("=" * 80)
    print("Selecione as informações que deseja ver na recomendação:")
    print()
    print("  [1] Análise do prato (parâmetros via Gemini AI)")
    print("  [2] Perfil fuzzy calculado")
    print("  [3] Dados do vinho (nome, uva, região, etc.)")
    print("  [4] Características do vinho (acidez, corpo, doçura)")
    print("  [5] Justificativa da harmonização")
    print("  [6] Outras harmonizações sugeridas")
    print()
    print("Digite os números das opções desejadas separados por vírgula")
    print("(Ex: 1,3,5  ou  all para todas)")
    print_separator()
    
    user_input = input("Opções: ").strip().lower()
    
    if user_input == "all" or user_input == "":
        return {1, 2, 3, 4, 5, 6}
    
    try:
        selected = set()
        for item in user_input.split(','):
            num = int(item.strip())
            if 1 <= num <= 6:
                selected.add(num)
        
        if not selected:
            print("⚠️  Nenhuma opção válida selecionada. Mostrando todas.")
            return {1, 2, 3, 4, 5, 6}
        
        return selected
    except ValueError:
        print("⚠️  Entrada inválida. Mostrando todas as opções.")
        return {1, 2, 3, 4, 5, 6}

def sanitize_input(text: str) -> str:
    """
    Sanitiza entrada do usuário removendo caracteres potencialmente perigosos
    """
    # Remove caracteres de controle e mantém apenas caracteres imprimíveis
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return sanitized.strip()

def validate_dish_description(description: str) -> bool:
    """
    Valida a descrição do prato
    """
    if not description:
        print("[!] Erro: Descricao do prato nao pode estar vazia.")
        return False
    
    if len(description) < MIN_DISH_DESCRIPTION_LENGTH:
        print(f"[!] Erro: Descricao muito curta. Use pelo menos {MIN_DISH_DESCRIPTION_LENGTH} caracteres.")
        return False
    
    if len(description) > MAX_DISH_DESCRIPTION_LENGTH:
        print(f"[!] Erro: Descricao muito longa. Use no maximo {MAX_DISH_DESCRIPTION_LENGTH} caracteres.")
        return False
    
    # Verificar se tem pelo menos uma letra (não é apenas números ou símbolos)
    if not re.search(r'[a-zA-ZÀ-ÿ]', description):
        print("[!] Erro: Descricao deve conter pelo menos uma palavra.")
        return False
    
    return True

def print_dish_params(params, show=True):
    if not show:
        return
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

def print_fuzzy_profile(perfil, show=True):
    if not show:
        return
    print(f"\n🔍 PERFIL FUZZY CALCULADO:")
    print_separator()
    print(f"  Categoria: {perfil['categoria'].upper()}")
    print(f"  Valor:     {perfil['valor']:.2f}/10")
    print_separator()

def print_recommendation(wine, options):
    print("\n🍾 VINHO RECOMENDADO:")
    print("=" * 80)
    
    if 3 in options:
        print(f"  Nome:              {wine['nome']}")
        print(f"  Uva:               {wine['uva']}")
        print(f"  Tipo:              {wine['tipo'].capitalize()}")
        print(f"  País:              {wine['país']}")
        print(f"  Região:            {wine['região']}")
        print(f"  Teor Alcoólico:    {wine['teor_alcoolico']}%")
        print_separator()
    
    if 4 in options:
        print(f"  Acidez:            {wine['acidez']}/10")
        print(f"  Corpo:             {wine['corpo']}/10")
        print(f"  Doçura:            {wine['doçura']}/10")
        print(f"  Intensidade Sabor: {wine['intensidade_sabor']}/10")
        print_separator()
    
    if 5 in options:
        print(f"\n💡 POR QUE ESSA HARMONIZAÇÃO?")
        print_separator()
        
        # Formatar justificativa com quebras de linha adequadas
        justificativa = wine['justificativa']
        paragraphs = justificativa.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # Quebrar linhas longas em 80 caracteres
                words = paragraph.strip().split()
                line = "  "
                for word in words:
                    if len(line) + len(word) + 1 <= 78:
                        line += word + " "
                    else:
                        print(line.rstrip())
                        line = "  " + word + " "
                print(line.rstrip())
                
                # Adicionar espaço entre parágrafos (exceto no último)
                if i < len(paragraphs) - 1:
                    print()
        
        print_separator()
    
    if 6 in options:
        print(f"\n🍽️  OUTRAS HARMONIZAÇÕES:")
        print(f"  {wine['harmonizacoes']}")
    
    print("=" * 80)

def visualize_rules(fuzzy_engine):
    """Exibe as regras fuzzy geradas"""
    print("\n📊 REGRAS FUZZY GERADAS AUTOMATICAMENTE")
    print("=" * 80)
    print()
    
    rules = fuzzy_engine.get_rules_text()
    
    for rule in rules:
        print(f"  {rule}")
    
    print()
    print("=" * 80)
    input("\nPressione ENTER para voltar ao menu...")


def visualize_tree(fuzzy_engine):
    """Exibe a árvore de decisão"""
    print("\n🌳 ÁRVORE DE DECISÃO FUZZY")
    print("=" * 80)
    print()
    
    tree_text = fuzzy_engine.get_tree_visualization()
    print(tree_text)
    
    print("=" * 80)
    input("\nPressione ENTER para voltar ao menu...")


def show_statistics(fuzzy_engine):
    """Exibe estatísticas do modelo"""
    print("\n📈 ESTATÍSTICAS DO MODELO")
    print("=" * 80)
    print()
    
    stats = fuzzy_engine.get_statistics()
    
    if 'total_pratos' in stats:
        print(f"  Total de pratos analisados: {stats['total_pratos']}")
        print(f"  Total de regras geradas: {stats['total_regras']}")
        print(f"  Profundidade da árvore: {stats['profundidade_arvore']}")
        print()
        
        print("  Distribuição de categorias:")
        for cat, count in stats['distribuicao_categorias'].items():
            print(f"    - {cat}: {count} pratos")
        print()
        
        if 'importancia_atributos' in stats and stats['importancia_atributos']:
            print("  Importância dos atributos:")
            for attr, importance in stats['importancia_atributos'][:5]:
                print(f"    - {attr}: {importance:.4f}")
    else:
        print(f"  Total de regras: {stats.get('total_regras', 0)}")
        print(f"  Tipo: {stats.get('tipo', 'desconhecido')}")
    
    print()
    print("=" * 80)
    input("\nPressione ENTER para voltar ao menu...")


def recommend_wine_for_dish(fuzzy_engine, csv_path):
    """Processo de recomendação de vinho"""
    try:
        # Solicitar descrição do prato
        print("\nPor favor, descreva o prato para o qual deseja uma recomendação de vinho:")
        print("(Ex: 'Filé mignon grelhado com molho de cogumelos')")
        print()
        dish_description = input("🍽️  Prato: ").strip()
        
        # Sanitizar entrada
        dish_description = sanitize_input(dish_description)
        
        # Validar entrada
        if not validate_dish_description(dish_description):
            return
        
        # Obter opções de saída do usuário
        output_options = get_output_options()
        
        print("\n[...] Processando com Gemini AI...")
        logger.info(f"Iniciando analise para: {dish_description[:50]}...")
        
        # 1. Processar com LLM
        llm = LLMProcessor()
        dish_params = llm.analyze_dish(dish_description)
        
        print_dish_params(dish_params, show=1 in output_options)
        
        # 2. Calcular perfil fuzzy
        print("\n[...] Aplicando regras fuzzy aprendidas...")
        logger.info("Computando perfil fuzzy")
        perfil_fuzzy = fuzzy_engine.compute_wine_profile(dish_params)
        
        print_fuzzy_profile(perfil_fuzzy, show=2 in output_options)
        
        # 3. Recomendar vinho
        print("\n[...] Buscando o vinho ideal na base de dados...")
        logger.info("Buscando recomendacao de vinho")
        recommender = WineRecommender(str(csv_path))
        wine = recommender.recommend(dish_params, perfil_fuzzy)
        
        print_recommendation(wine, output_options)
        
        print("\n✅ Recomendação concluída com sucesso!\n")
        logger.info("Recomendacao concluida com sucesso")
        
        input("Pressione ENTER para voltar ao menu...")
        
    except ValueError as e:
        error_msg = f"Erro de validacao: {e}"
        print(f"\n❌ {error_msg}")
        logger.error(error_msg)
        input("\nPressione ENTER para voltar ao menu...")
    except Exception as e:
        error_msg = f"Erro inesperado: {e}"
        print(f"\n❌ {error_msg}")
        logger.exception("Erro inesperado durante execucao")
        input("\nPressione ENTER para voltar ao menu...")


def main():
    print_header()
    
    # Paths
    csv_path = root_dir / "data" / "vinhos.csv"
    dishes_csv_path = root_dir / "data" / "pratos.csv"
    
    try:
        # Inicializar Fuzzy Engine com aprendizado
        print("[...] Inicializando sistema e aprendendo regras dos pratos conhecidos...")
        fuzzy = FuzzyEngine(str(dishes_csv_path), use_learned_rules=True)
        print("✅ Sistema inicializado!\n")
        
        # Loop do menu principal
        while True:
            choice = get_main_menu_choice()
            
            if choice == '1':
                recommend_wine_for_dish(fuzzy, csv_path)
            elif choice == '2':
                visualize_rules(fuzzy)
            elif choice == '3':
                visualize_tree(fuzzy)
            elif choice == '4':
                show_statistics(fuzzy)
            elif choice == '5':
                print("\n👋 Obrigado por usar o sistema! Até logo!\n")
                break
            else:
                print("\n⚠️  Opção inválida. Tente novamente.")
                input("Pressione ENTER para continuar...")
        
    except FileNotFoundError as e:
        error_msg = f"Erro: Arquivo nao encontrado - {e}"
        print(f"\n❌ {error_msg}")
        logger.error(error_msg)
    except KeyboardInterrupt:
        print("\n\n❌ Operacao cancelada pelo usuario.")
        logger.info("Operacao cancelada pelo usuario")
    except Exception as e:
        error_msg = f"Erro inesperado: {e}"
        print(f"\n❌ {error_msg}")
        logger.exception("Erro inesperado durante execucao")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

