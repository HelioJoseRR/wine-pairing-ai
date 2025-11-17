import json

# ---------------------------
# CONFIGURAÇÃO DO MODELO
# ---------------------------

from openai import OpenAI
client = OpenAI(api_key="SUA_API_KEY_AQUI")


# ---------------------------
# PROMPT BASE PARA PARAMETRIZAÇÃO
# ---------------------------

PROMPT_PARAMETRIZAR = """
Você é um sistema que transforma pratos de comida em parâmetros sensoriais de 0 a 10.

Parâmetros definidos:
1. teor_gordura (0–10)
2. doçura (0–10)
3. sal (0–10)
4. acidez (0–10)
5. picancia (0–10)
6. aroma (0–10)
7. complexidade (0–10)
8. umidade (0–10)
9. maciez (0–10)
10. corpo (0–10)

Objetivo:
- Dado o nome de um prato, você deve estimar cada parâmetro baseado em conhecimento gastronômico real.
- A resposta DEVE ser um JSON válido contendo todos os 10 valores.

Formato EXATO da resposta:
{
  "teor_gordura": X,
  "doçura": X,
  "sal": X,
  "acidez": X,
  "picancia": X,
  "aroma": X,
  "complexidade": X,
  "umidade": X,
  "maciez": X,
  "corpo": X
}
"""


# ---------------------------
# FUNÇÃO: Chama a LLM para parametrizar o prato
# ---------------------------

def parametrizar_prato(nome_do_prato: str) -> dict:
    """
    Envia o nome do prato para a LLM e retorna os parâmetros estimados em formato JSON.
    """

    mensagem = PROMPT_PARAMETRIZAR + f'\n\nPrato: "{nome_do_prato}"\n\nResponda somente com o JSON.'

    response = client.chat.completions.create(
        model="gpt-4.1",   # coloque o modelo desejado
        messages=[
            {"role": "system", "content": "Você é um especialista em gastronomia e harmonização."},
            {"role": "user", "content": mensagem}
        ],
        temperature=0
    )

    resposta = response.choices[0].message["content"].strip()

    # Tenta converter para JSON
    try:
        parametros = json.loads(resposta)
    except json.JSONDecodeError:
        raise ValueError("A LLM não retornou um JSON válido:\n" + resposta)

    return parametros


# ---------------------------
# EXEMPLO DE USO
# ---------------------------

if __name__ == "__main__":
    prato = input("Digite o nome do prato: ")
    params = parametrizar_prato(prato)
    print("\nParâmetros estimados:")
    print(json.dumps(params, indent=4))
