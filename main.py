# ==========================================
# 1. Setup e Imports
# ==========================================
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import scipy.stats as stats
from groq import Groq # API Groq
import re
import string

# ==========================================
# 2. Fase 1: Coleta de dados CN (Humanos)
# ==========================================

# Lista estável de 100 IDs do Gutenberg (Clássicos Populares em Inglês)
GUTENBERG_IDS = [
    1342, 84, 11, 1661, 2701, 145, 2600, 345, 98, 46, 844, 174, 120, 2542, 1952, 
    219, 160, 5200, 1184, 4300, 28054, 1400, 2554, 76, 55, 2814, 158, 205, 1260, 
    161, 36, 1232, 1497, 45, 215, 244, 3207, 74, 100, 2148, 8800, 1998, 1727, 
    30254, 113, 236, 42324, 25344, 135, 35, 119, 521, 203, 1080, 14838, 2591, 
    308, 1250, 408, 41, 16, 1399, 153, 514, 1581, 121, 141, 768, 541, 27827, 
    43, 2097, 3825, 2641, 2852, 996, 851, 1934, 1404, 3021, 16328, 580, 105, 
    3176, 1322, 1064, 4363, 164, 18581, 972, 1787, 829, 35534, 31100, 40438, 
    18857, 1063, 2489, 34040, 2346
]

def download_gutenberg(book_id):
    """Faz o download automatizado da obra em formato .txt"""
    url = f"https://gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Verifica se houve erro HTTP
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar ID {book_id}: {e}")
        return None

def clean_gutenberg_text(text):
    """Limpa o texto: remove cabeçalho/rodapé do Gutenberg, pontuações e números"""
    # Isolar o conteúdo real do livro removendo metadados do Gutenberg
    start_match = re.search(r'\*\*\* START OF THE PROJECT GUTENBERG.*?\*\*\*', text, re.IGNORECASE)
    end_match = re.search(r'\*\*\* END OF THE PROJECT GUTENBERG.*?\*\*\*', text, re.IGNORECASE)
    
    if start_match and end_match:
        text = text[start_match.end():end_match.start()]
    elif start_match:
        text = text[start_match.end():]
        
    # Converter para minúsculas
    text = text.lower()
    
    # Manter apenas letras e espaços (remove pontuação e números)
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    # Remover espaços em branco extras
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_n_words(text, n=25000):
    """Extrai exatamente n palavras do texto"""
    words = text.split()
    if len(words) >= n:
        return words[:n]
    else:
        return None # Retorna None se o livro for muito curto

# ==========================================
# Execução do Pipeline da Fase 1
# ==========================================
corpus_cn = {} # Dicionário para armazenar {id: [lista_de_palavras]}

print("Iniciando Fase 1: Coleta de Dados CN...")
for b_id in GUTENBERG_IDS:
    raw_text = download_gutenberg(b_id)
    
    if raw_text:
        cleaned_text = clean_gutenberg_text(raw_text)
        words_list = extract_n_words(cleaned_text, n=25000)
        
        if words_list:
            corpus_cn[b_id] = words_list
            print(f"Livro ID {b_id} processado com sucesso!")
        else:
            print(f"Livro ID {b_id} descartado (menos de 25.000 palavras).")
            
print(f"\nColeta finalizada! Total de livros válidos coletados (CN): {len(corpus_cn)}")