import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Cargar archivo CSV previamente procesado
file_path = "Resumen_GOLD_procesado_CHGPT.csv"
df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')

# Convertir términos a listas
default_term = ["Normal"]
for column in df.columns[1:]:
    df[column] = df[column].apply(lambda x: x.split('|') if x else [])

# Modelo semántico
model = SentenceTransformer('all-MiniLM-L6-v2')

# Función TP, FP y FN
def compute_embedding_tp_fp_fn(gold_terms, hypothesis_terms, threshold=0.7):
    gold_embeddings = model.encode(gold_terms)
    hypothesis_embeddings = model.encode(hypothesis_terms)

    tp, fp = 0, 0
    for h_emb in hypothesis_embeddings:
        similarities = cosine_similarity([h_emb], gold_embeddings).flatten()
        if max(similarities) >= threshold:
            tp += 1
        else:
            fp += 1

    fn = max(len(gold_terms) - tp, 0)

    return tp, fp, fn

threshold=0.5
# Análisis y resultados
results = []
for _, row in df.iterrows():
    gold_terms = row["Gold"]
    for hyp_col in ['NN', 'DN', 'ND', 'DD']:
        hypothesis_terms = row[hyp_col]
        tp, fp, fn = compute_embedding_tp_fp_fn(gold_terms, hypothesis_terms, threshold=threshold)
        results.append({
            'ID': row['ID'],
            'Hipótesis': hyp_col,
            'TP': tp,
            'FP': fp,
            'FN': fn
        })

# Guardar resultados
results_df = pd.DataFrame(results)
results_df.to_csv("resultados_embeddings_"+str(threshold)+".csv", index=False, encoding='utf-8', sep=';')

print(results_df)
