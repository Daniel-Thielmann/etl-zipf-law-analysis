import os
import time
import re
from groq import Groq
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env automaticamente para o os.environ
load_dotenv()

# Puxa a chave de forma segura
API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "2500"))

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY não encontrada. Defina a chave no arquivo .env ou nas variáveis de ambiente."
    )

client = Groq(api_key=API_KEY)


def save_prompt_to_md(book_id, prompt_text):
    """Salva o prompt utilizado em um arquivo .md para reprodutibilidade."""
    os.makedirs("prompts", exist_ok=True)
    with open(f"prompts/prompt_livro_{book_id}.md", "w", encoding="utf-8") as f:
        f.write(prompt_text)


def generate_artificial_text(book_id, human_words, max_retries=5):
    """
    Gera o gêmeo artificial via Groq. Implementa backoff exponencial e fallback.
    """
    sample_start = " ".join(human_words[:35])
    sample_mid = " ".join(human_words[12500:12535])

    prompt = f"""
    Write a long, creative narrative in English that mimics the style, vocabulary, and thematic elements of the following text samples. 
    Sample 1: "{sample_start}"
    Sample 2: "{sample_mid}"
    The generated text must be extensive, continuous prose without any markdown formatting, titles, or numbers.
    """

    save_prompt_to_md(book_id, prompt)
    base_wait_time = 2

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a classic literature author.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=GROQ_MODEL,
                temperature=0.7,
                max_tokens=GROQ_MAX_TOKENS,
            )

            generated_text = response.choices[0].message.content
            if not generated_text:
                raise ValueError("Groq retornou conteúdo vazio.")
            cleaned_ca = re.sub(r"[^a-z\s]", " ", generated_text.lower())
            cleaned_ca = re.sub(r"\s+", " ", cleaned_ca).strip()

            ca_words = cleaned_ca.split()
            print(f"ID {book_id}: IA gerou {len(ca_words)} palavras com sucesso.")
            return ca_words

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str:
                wait_time = base_wait_time * (2**attempt)
                print(
                    f"Rate limit no ID {book_id}. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                print(f"Erro inesperado na API para o ID {book_id}: {e}")
                break

    # Se sair do loop de retries ou der break em um erro que não seja Rate Limit
    print(
        f"Falha irrecuperável na geração para o ID {book_id}. Acionando Fallback (clonagem do corpus natural)."
    )
    return human_words.copy()
