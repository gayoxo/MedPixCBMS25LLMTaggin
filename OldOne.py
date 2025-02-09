import sys

# Verificar si se pasó un argumento para el nombre del archivo
if len(sys.argv) != 2:
    print("Uso: python3 indiana_one_All.py <nombre_del_archivo>")
    sys.exit(1)

    # Obtener el nombre del archivo del primer argumento
filename = sys.argv[1]

import warnings

warnings.filterwarnings("ignore")

from ollama import Client

# Lista para almacenar el historial de conversación
historial_mensajes = []


def obtener_respuesta(valor_texto):
    try:
        client = Client(host='http://maths.fdi.ucm.es:11434')
    except Exception as e:
        print(f"Error conectarse a la API de OLLAAMA: {e}")
        return None

    content_text = 'Assuming that for this text: "Dyspnea. Cardiomediastinal silhouette and pulmonary vasculature are within normal limits. Lungs are clear. No pneumothorax or pleural effusion. Evidence of prior granulomatous disease. No acute osseous findings. No acute cardiopulmonary findings." \n\nThe result of the diseases and findings in JSON is: [{"finding": "Prior granulomatous disease"}, {"finding": "Pneumothorax", "absent": true}, {"finding": "Pleural effusion", "absent": true}, {"finding": "Acute osseous findings", "absent": true}, {"finding": "Acute cardiopulmonary findings", "absent": true}, {"finding": "Dyspnea"}, {"finding": "cardiomediastinal silhouette normal"}, {"finding": "pulmonary vasculature normal"}, {"finding": "lung clear"}] \n\nCould you do the same search for elements in the following text:' + valor_texto + ' and return only the JSON response same as previous result. Please make sure the JSON is valid remembering the True boolean value in JSON should be declared as true in lowercase'

    response = client.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': content_text,
        },
    ])

    if response:
        #        historial_mensajes.append({
        #                'role': 'assistant',
        #                'content': response['message']['content']
        #            })
        # print(response)
        return response
    else:
        #  print("No se recibió respuesta")
        return None


import re
import json


def extract_json(text):
    try:
        # Busca cualquier bloque de texto que parezca un JSON (entre corchetes o llaves)
        json_match = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            # Intenta cargarlo como un objeto JSON
            parsed_json = json.loads(json_text)
            return parsed_json
        else:
            # print("No se encontró un JSON en el texto.")
            return None
    except json.JSONDecodeError as e:
        # print(f"Error al decodificar JSON: {e}")
        return fix_json_with_ollama(json_text)


import subprocess


def fix_json_with_ollama(json_text):
    """
    Función para verificar y reparar un JSON usando Ollama.
    """
    try:
        # Primero, intenta cargar el JSON directamente
        return json.loads(json_text)
    except json.JSONDecodeError:
        # print("JSON no válido. Usando Ollama para repararlo...")
        pass

    client = Client(host='http://maths.fdi.ucm.es:11434')

    # Formatear el prompt para Ollama
    prompt = f"""
        The following text is supposed to be a JSON, but it may have issues. 
        Please validate, fix it, and return the corrected JSON only:

        {json_text}
    """

    # Ejecutar el modelo de Ollama
    response = client.chat(model='qwen2.5-coder', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])

    # Procesar la salida
    json_response = response['message']['content'].strip()
    try:
        # Intentar decodificar el JSON reparado
        return json.loads(json_response)
    except json.JSONDecodeError:
        #  print("No se pudo reparar el JSON con Ollama.")
        #  print(json_text)
        return None


def desanonimizar_informe_medico(texto_anonimizado):
    try:
        client = Client(host='http://maths.fdi.ucm.es:11434')
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


import kagglehub

# Download latest version
path = kagglehub.dataset_download("raddar/chest-xrays-indiana-university")

# print("Path to dataset files:", path);

import csv

# Abre el archivo CSV
with open(path + '/indiana_reports.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)

    # Inicializa un contador de filas
    valid_row_count = 0

    # JSON data:
    JsonResFinalStr = '[]'

    # parsing JSON string:
    JsonResFinal = {"result": []}

    # Salta la cabecera
    next(reader)

    # Itera sobre cada línea y limita a las primeras 10 filas
    for row in reader:
        # Obtén las columnas 5, 7 y 8 (índices 4, 6 y 7 en base 0)
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

        # Verifica si el texto combinado tiene más de 10 caracteres
        if len(combined_string) > 10:

            if "XXXX" in combined_string:
                print(combined_string + "->Limpiar")
                combined_string = desanonimizar_informe_medico(combined_string)
                # print(combined_string + "<-Resultado")
                anon = True

            # print(col1)
            # print(valid_row_count)

            # Imprime el resultado si es válido
            print(combined_string)

            valid = False
            counter = 1

            while not valid and counter < 3:
                resultado = obtener_respuesta(combined_string)['message']['content']
                resultadoJSON = extract_json(resultado)
                if resultadoJSON is not None and len(resultadoJSON) > 0:
                    objeto = {"raw": combined_string}
                    objeto["set"] = resultadoJSON
                    print(resultadoJSON)
                    if anon:
                        objeto["des_anon"] = True
                        objeto["raw_ori"] = combined_string_original
                        valid2 = False
                        counter2 = 1
                        while not valid2 and counter2 < 3:
                            resultadoAnon = obtener_respuesta(combined_string_original)['message']['content']
                            resultadoJSONAnnon = extract_json(resultadoAnon)
                            print(resultadoJSONAnnon)
                            if resultadoJSONAnnon is not None and len(resultadoJSONAnnon) > 0:
                                objeto["set_ori"] = resultadoJSONAnnon
                                valid2 = True
                            else:
                                counter2 = counter2 + 1

                    JsonResFinal["result"].append(objeto)
                    valid = True
                else:
                    counter = counter + 1
                    # print("reintentando" + counter )

            if valid:
                # Incrementa el contador de filas válidas
                valid_row_count += 1

    # json_str = sjson.dumps(JsonResFinal, indent=4, sort_keys=True)
    # print(json_str)
    # print(json.dumps(JsonResFinal))
    try:
        with open(filename, 'w') as file:
            json.dump(JsonResFinal, file, indent=4)
        print(f"JSON guardado exitosamente en {filename}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
