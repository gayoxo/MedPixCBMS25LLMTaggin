from ollama import Client
import re
import json

# Lista para almacenar el historial de conversación


def obtener_respuesta(valor_texto, historial_mensajes=[], jsonIni={}):
    try:
        client = Client(host='http://localhost:11434')
    except Exception as e:
        print(f"Error conectarse a la API de OLLAAMA: {e}")
        return None

    content_text = (
        f"""Extract all **clinically relevant findings and diseases** from the following medical text.

Return **only** a valid JSON array, merging the findings with the existing list in `jsonIni`, ensuring that:
- **No duplicate terms** are included.
- **Only medically relevant findings and diseases** are extracted.
- **Irrelevant terms, normal findings, and anatomical descriptions are excluded**.

### Input:
1. `jsonIni`: {jsonIni}  # Initial list of findings and diseases.
2. Text to analyze:
   {valor_texto}

### Output format:
- Each object in the JSON array must include:
  - `"finding"`: the **clinically significant finding or disease** identified in the text.

### Important:
- **Ensure all values are clinically relevant.**
- **Exclude** general observations, normal findings, and anatomical descriptions such as:
  - "Unremarkable structures"
  - "Normal appearance"
  - "No abnormalities detected"
  - "Mild age-related changes"
  - "Typical anatomy"
  - "No significant pathology"
- Maintain lowercase `"true"` for boolean values.
- **DO NOT** include any explanations, code, or additional text—return **only** the JSON array."""

    )

    #print(content_text)

    response = client.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': content_text,
        },
    ])

    if response:
        historial_mensajes.append({
                'role': 'assistant',
                'content': response['message']['content']
                })
        # print(response)
        return historial_mensajes, response
    else:
        #  print("No se recibió respuesta")
        return None


def mergeJSON(json1,json2) :

    if json1 is None :
        return json2

    # Convertir en un diccionario para evitar duplicados (clave = "finding")
    merged_dict = {entry["finding"]: entry for entry in json1}

    # Agregar los elementos de json2 sin duplicar
    for entry in json2:
        merged_dict[entry["finding"]] = entry

    # Convertir nuevamente en lista
    merged_json = list(merged_dict.values())

    return merged_json

def extract_json(text):
    try:
        # Busca cualquier bloque de texto que parezca un JSON (entre corchetes o llaves)
        json_match = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            #print("jsonfound->",json_text)
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

    client = Client(host='http://localhost:11434')

    # Formatear el prompt para Ollama
    prompt = f"""
        The following text is supposed to be a JSON, but it may have issues. 
        Please validate, fix it, and return the corrected JSON only:

        {json_text}
    """

    # Ejecutar el modelo de Ollama
    response = client.chat(model='qwen2.5-coder:0.5b', messages=[
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

def intentoBase(textOri,historial_mensajes,resultadoJSONAnnon):
    if resultadoJSONAnnon is not None:
        historial_mensajes, resultadoAnon = obtener_respuesta(textOri, historial_mensajes, resultadoJSONAnnon)
    else :
        historial_mensajes, resultadoAnon = obtener_respuesta(textOri, historial_mensajes)

    #print(f"Historial_mensajes: {historial_mensajes}")
    #print(f"Texto resultadoAnon: {resultadoAnon['message']['content']}")
    resultadoJSONAnnon2 = extract_json(resultadoAnon['message']['content'])
    return resultadoJSONAnnon2, resultadoAnon['message']['content']

# Leer el archivo JSON desanonimizado
archivo_salida = "resultados_desanonimizados.json"
with open(archivo_salida, "r", encoding="utf-8") as f:
    datos = json.load(f)

# Crear las listas de textOri y textDesa
lista_textOri = [objeto["textOri"] for objeto in datos]
lista_textDesa = [objeto["textDesa"] for objeto in datos]

# Imprimir los resultados
#print("Lista de textOri:", lista_textOri)
#print("Lista de textDesa:", lista_textDesa)

# Recorrer la lista de textOri con un bucle
print("Recorriendo textOri:")

ResultadoErrores=[]

historial_mensajes=[]
resultadoJSONAnnon= None
for textOri in lista_textOri:

    resultadoJSONAnnon2, resultadoContent = intentoBase(textOri, historial_mensajes,resultadoJSONAnnon)

    if resultadoJSONAnnon2 is not None:
        resultadoJSONAnnon=mergeJSON(resultadoJSONAnnon,resultadoJSONAnnon2)
    else:
        resultadoJSONAnnon2, resultadoContent = intentoBase(textOri, historial_mensajes, resultadoJSONAnnon)

        if resultadoJSONAnnon2 is not None:
            resultadoJSONAnnon = mergeJSON(resultadoJSONAnnon, resultadoJSONAnnon2)
        else:
            resultadoJSONAnnon2, resultadoContent = intentoBase(textOri, historial_mensajes, resultadoJSONAnnon)

            if resultadoJSONAnnon2 is not None:
                resultadoJSONAnnon = mergeJSON(resultadoJSONAnnon, resultadoJSONAnnon2)
            else:
                dictvalor=dict();
                dictvalor["text"] = textOri
                dictvalor["res"] = resultadoContent
                ResultadoErrores.append(dictvalor)
                print("not found", resultadoContent)

    #print(f"Texto Original: {textOri}")
    print(f"Texto JSON: {resultadoJSONAnnon}")
    #print("---")

print(f"Texto JSON: {resultadoJSONAnnon}")

# Nombre del archivo donde se guardará el JSON
archivo_salida = "resultadoFinalNormal.json"

# Guardar el JSON en el archivo
with open(archivo_salida, "w", encoding="utf-8") as f:
    json.dump(resultadoJSONAnnon, f, indent=4, ensure_ascii=False)

print(f"JSON guardado en {archivo_salida}")



# Recorrer la lista de textOri con un bucle
print("Recorriendo lista_textDesa:")

historial_mensajes2=[]
resultadoJSONAnnon= None
for textOri in lista_textDesa:

    resultadoJSONAnnon2, resultadoContent = intentoBase(textOri, historial_mensajes2,resultadoJSONAnnon)

    if resultadoJSONAnnon2 is not None:
        resultadoJSONAnnon=mergeJSON(resultadoJSONAnnon,resultadoJSONAnnon2)
    else:
        resultadoJSONAnnon2, resultadoContent = intentoBase(textOri, historial_mensajes2, resultadoJSONAnnon)

        if resultadoJSONAnnon2 is not None:
            resultadoJSONAnnon = mergeJSON(resultadoJSONAnnon, resultadoJSONAnnon2)
        else:
            resultadoJSONAnnon2, resultadoContent = intentoBase(textOri, historial_mensajes2, resultadoJSONAnnon)

            if resultadoJSONAnnon2 is not None:
                resultadoJSONAnnon = mergeJSON(resultadoJSONAnnon, resultadoJSONAnnon2)
            else:
                dictvalor = dict();
                dictvalor["text"] = textOri
                dictvalor["res"] = resultadoContent
                ResultadoErrores.append(dictvalor)
                print("not found", resultadoContent)

    #print(f"Texto Original: {textOri}")
    print(f"Texto JSON: {resultadoJSONAnnon}")
    #print("---")

print(f"Texto JSON: {resultadoJSONAnnon}")

# Nombre del archivo donde se guardará el JSON
archivo_salida = "resultadoFinalAnnon.json"

# Guardar el JSON en el archivo
with open(archivo_salida, "w", encoding="utf-8") as f:
    json.dump(resultadoJSONAnnon, f, indent=4, ensure_ascii=False)

print(f"JSON guardado en {archivo_salida}")


# Nombre del archivo donde se guardará el JSON
archivo_salida = "resultadoErrores.json"

# Guardar el JSON en el archivo
with open(archivo_salida, "w", encoding="utf-8") as f:
    json.dump(ResultadoErrores, f, indent=4, ensure_ascii=False)

print(f"Errores guardados en {archivo_salida}")