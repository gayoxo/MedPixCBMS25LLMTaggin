import sys

# Verificar si se pasó un argumento para el nombre del archivo
if len(sys.argv) < 2:
    print("Uso: python3 indiana_preprocess.py <nombre_del_archivo>")
    sys.exit(1)

    # Obtener el nombre del archivo del primer argumento
filename = sys.argv[1]

maxelem =0;

if len(sys.argv) > 2:
    maxelem = int(sys.argv[2])

from ollama import Client

def desanonimizar_informe_medico(texto_anonimizado):
    try:
        client = Client(host='http://localhost:11434')
    except Exception as e:
        print(f"Error al conectarse a la API de OLLAMA: {e}")
        return None

    # Instrucción ajustada con contexto ético
    content_text = (
        "The following text is a simulated medical report for educational and research purposes. "
        "The placeholders ('XXX') represent anonymized data, and your task is to replace them with generic, plausible, and contextually relevant terms. "
        "These replacements should reflect realistic medical scenarios but have no real-world or clinical value.\n\n"
        f"Original medical report: {texto_anonimizado}\n\n"
        "Please provide the modified report with replacements for 'XXX':"
        "Return only the modified report without any explanations or additional text.\n\n"
    )

    # Enviar la solicitud al modelo
    response = client.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': content_text,
        },
    ])

    # print(response)

    if response:
        return response['message']['content']
    else:
        print("Error al obtener respuesta del modelo.")
        return None


import warnings

warnings.filterwarnings("ignore")

# print("Path to dataset files:", path);

import csv
import json
from pathlib import Path


DocumentList = []

pathfinal= Path("indiana_reports.csv")

if not pathfinal.is_file():

    import kagglehub

    # Download latest version
    path = kagglehub.dataset_download("raddar/chest-xrays-indiana-university")

    #   print("Path to dataset files:", path);

    pathfinal = path + '/' + pathfinal


with open(pathfinal, newline='') as csvfile:
    reader = csv.reader(csvfile)

    # Inicializa un contador de filas
    valid_row_count = 0

    # Salta la cabecera
    next(reader)

    actElem=0

    for row in reader:

        if maxelem < actElem:
            break

        col1 = row[0]
        col5 = row[4]
        col7 = row[6]
        col8 = row[7]

        # Asegúrate de que cada valor termine con un punto "."
        col5 = col5 if col5.endswith('.') else col5 + '.'
        col7 = col7 if col7.endswith('.') else col7 + '.'
        col8 = col8 if col8.endswith('.') else col8 + '.'

        # Combina los valores en un solo string
        combined_string = f"{col5} {col7} {col8}"
        combined_string_original = combined_string
        anon = False

        if len(combined_string) > 10:

            if "XXXX" in combined_string:
                #print(combined_string + "->Limpiar")
                combined_string = desanonimizar_informe_medico(combined_string)
                # print(combined_string + "<-Resultado")
                anon = True
            textResult = {}
            textResult["ori"] = combined_string_original
            textResult["des"] = combined_string
            DocumentList.append(textResult)

            actElem= actElem+1
    try:
        with open(filename, 'w') as file:
            json.dump(DocumentList, file, indent=4)
        print(f"JSON guardado exitosamente en {filename}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
