import pandas as pd

# Cargar resultados previamente calculados (que ya incluyen FN)
results_df = pd.read_csv("resultados_embeddings_0.7.csv", delimiter=';', encoding='utf-8')

# Agrupar resultados por hipótesis
summary = results_df.groupby('Hipótesis').sum().reset_index()

# Eliminar columna ID si existe tras la agrupación
summary = summary.drop(columns=['ID'], errors='ignore')

# Calcular métricas
summary['Precision'] = summary['TP'] / (summary['TP'] + summary['FP'])
summary['Recall'] = summary['TP'] / (summary['TP'] + summary['FN'])
summary['F1-Score'] = 2 * (summary['Precision'] * summary['Recall']) / (summary['Precision'] + summary['Recall'])

# Guardar métricas completas en CSV
summary.to_csv("metricas_precision_recall_f1_completas_0.7.csv", index=False, sep=';', encoding='utf-8')

# Mostrar los resultados
print(summary)
