import pandas as pd
from pathlib import Path
from pre_processing import download_gutenberg, clean_gutenberg_text, extract_n_words
from llm_generation import generate_artificial_text


def main():
    # Carregar os 100 IDs validados do CSV
    try:
        csv_path = Path(__file__).with_name("gutenberg_ids.csv")
        df_ids = pd.read_csv(csv_path)
        GUTENBERG_IDS = df_ids["book_id"].tolist()
    except FileNotFoundError:
        print(
            "Arquivo gutenberg_ids.csv não encontrado. Certifique-se de que ele está na raiz do projeto."
        )
        return
    except KeyError:
        print(
            "Coluna 'book_id' não encontrada em gutenberg_ids.csv. Verifique o cabeçalho do arquivo."
        )
        return

    corpus_cn = {}
    corpus_ca = {}

    print("=== INICIANDO PIPELINE DE MODELAGEM ===")

    for i, b_id in enumerate(GUTENBERG_IDS, start=1):
        print(f"\n--- Processando ID: {b_id} ({i}/100) ---")

        # Fase 1: Coleta e Limpeza (Pre-processing)
        raw_text = download_gutenberg(b_id)
        if not raw_text:
            continue

        cleaned_text = clean_gutenberg_text(raw_text)
        human_words = extract_n_words(cleaned_text, n=25000)

        if human_words:
            corpus_cn[b_id] = human_words
            print(f"ID {b_id}: Coleta Humana (CN) OK.")

            # Fase 2: Geração via LLM
            artificial_words = generate_artificial_text(b_id, human_words)
            corpus_ca[b_id] = artificial_words
        else:
            print(f"ID {b_id} descartado na validação (menos de 25k palavras).")

    print(f"\n=== PIPELINE DE COLETA E GERAÇÃO FINALIZADO ===")
    print(f"Total CN: {len(corpus_cn)} livros.")
    print(f"Total CA: {len(corpus_ca)} textos sintéticos.")


if __name__ == "__main__":
    main()
