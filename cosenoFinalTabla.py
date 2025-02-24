import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Cargar archivo CSV procesado
file_path = "Resumen_GOLD_procesado_CHGPT.csv"
df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')

# Convertir términos a listas
default_term = ["Normal"]
for column in df.columns[1:]:
    df[column] = df[column].apply(lambda x: x.split('|') if x else [])

# Modelo semántico
model = SentenceTransformer('all-MiniLM-L6-v2')

# Crear tabla de similitud
similarity_results = []

for _, row in df.iterrows():
    gold_terms = row["Gold"]
    gold_embeddings = model.encode(gold_terms)

    for hyp_col in ['NN', 'DN', 'ND', 'DD']:
        hypothesis_terms = row[hyp_col]
        hypothesis_embeddings = model.encode(hypothesis_terms)

        for idx_h, h_emb in enumerate(hypothesis_embeddings):
            similarities = cosine_similarity([h_emb], gold_embeddings).flatten()
            for idx_g, similarity in enumerate(similarities):
                similarity_results.append({
                    'ID': row['ID'],
                    'Hipótesis': hyp_col,
                    'Término Hipótesis': hypothesis_terms[idx_h],
                    'Término Gold': gold_terms[idx_g],
                    'Similitud Coseno': similarity
                })

# Guardar la tabla de similitudes en CSV
similarity_df = pd.DataFrame(similarity_results)
similarity_df.to_csv("tabla_similitud_coseno.csv", index=False, encoding='utf-8', sep=';')

# Mostrar resultados
print(similarity_df.head())
