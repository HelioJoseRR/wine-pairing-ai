#!/usr/bin/env python3
"""
Script de teste para demonstrar a nova justificativa expandida com Gemini
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.recommender import WineRecommender

# Simular parâmetros de um prato (exemplo: Filé Mignon grelhado)
dish_params = {
    'proteina': 9.0,
    'gordura': 7.0,
    'acidez': 3.0,
    'dulcor': 1.0,
    'intensidade_sabor': 8.5,
    'crocancia': 2.0,
    'metodo_preparo': 9.0,
    'especiarias': 5.0,
    'teor_umami': 8.0,
    'nivel_salgado': 6.0
}

perfil_fuzzy = {
    'valor': 8.2,
    'categoria': 'encorpado'
}

print("=" * 70)
print("🧪 TESTE: Justificativa Expandida com Gemini")
print("=" * 70)
print("\n📊 Prato simulado: Filé Mignon grelhado com cogumelos\n")

csv_path = root_dir / "data" / "vinhos.csv"
recommender = WineRecommender(str(csv_path))

if recommender.use_llm_justification:
    print("✓ Gemini API configurada - gerando justificativa expandida...\n")
else:
    print("⚠ Gemini API não configurada - usando justificativa simples\n")

wine = recommender.recommend(dish_params, perfil_fuzzy)

print("=" * 70)
print(f"🍾 Vinho: {wine['nome']}")
print("=" * 70)
print(f"\n💡 JUSTIFICATIVA:\n")
print(wine['justificativa'])
print("\n" + "=" * 70)
