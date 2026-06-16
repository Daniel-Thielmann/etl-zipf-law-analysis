import requests
import re


def download_gutenberg(book_id):
    """Faz o download automatizado da obra em formato .txt"""
    url = f"https://gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar ID {book_id}: {e}")
        return None


def clean_gutenberg_text(text):
    """Limpa o texto: remove cabeçalho/rodapé do Gutenberg, pontuações e números"""
    start_match = re.search(
        r"\*\*\* START OF THE PROJECT GUTENBERG.*?\*\*\*", text, re.IGNORECASE
    )
    end_match = re.search(
        r"\*\*\* END OF THE PROJECT GUTENBERG.*?\*\*\*", text, re.IGNORECASE
    )

    if start_match and end_match:
        text = text[start_match.end() : end_match.start()]
    elif start_match:
        text = text[start_match.end() :]

    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_n_words(text, n=25000):
    """Extrai exatamente n palavras do texto"""
    words = text.split()
    if len(words) >= n:
        return words[:n]
    else:
        return None
