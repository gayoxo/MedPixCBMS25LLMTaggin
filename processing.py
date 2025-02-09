from ollama import Client
import re
import json

def obtener_respuesta(valor_texto, historial_mensajes=[], jsonIni={}):
    try:
        client = Client(host='http://localhost:11434')
    except Exception as e:
        print(f"Error conectarse a la API de OLLAAMA: {e}")
        return None

    content_text = (
        f"""
        
        Assuming you are in a medical enviroment.
        
        Extract only **clinically significant findings and diseases** from the following medical text whit apear as 
        positive in the description of the patient record.

        **Strictly return only a valid JSON array** with clinically relevant conditions appear in the text with 
        expecial detail in not include terms about normal situations in the human body. Remove absent or in 
        normal limit findings and diseases from the result.  Take care to not include terms not presents or appear in the text.

        ### **Rules:**
        1. **Only include findings or diseases that indicate pathology**.
        2. **Exclude normal findings, general observations, and anatomical descriptions**, including:
           - Normal anatomical structures
           - Expected age-related changes
           - Terms indicating **absence of disease**, such as:
             - "No abnormality detected"
             - "Unremarkable"
             - "Within normal limits"
            -Remove absent terms or in normal limits of findings and diseases from the result.
            -Take care to not include terms not presents or appear in the text.
        3. **Ensure clinical relevance** by only including terms present in `jsonIni`and not absent or in normal limits.

        ### **Input:**
        - `jsonIni`: {jsonIni}  # List of clinically relevant findings and diseases.
        - Medical text to analyze:
          {valor_texto}

        ### **Output Format (JSON Array):**
        - Each object in the JSON array **must include**:
          - `"finding"`: the **clinically significant** term extracted from the text.

        ### **Additional Constraints:**
        - **DO NOT return normal findings, anatomical structures, or mild changes.**
        - **DO NOT add extra text, explanations, or invalid JSON.**
        - Ensure the output is a **well-formatted JSON array**.
        - Be care to include information not-well sure about finding appear in the text, only return elemento cleary 
        apear in the medical text.
        """
    )

    #print(content_text)

    print(valor_texto)

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
        print(response['message']['content'])
        return historial_mensajes, response
    else:
        #  print("No se recibió respuesta")
        return None


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

def intentoBase(textOri, historial_mensajes,resultadoJSONAnnon):

    historial_mensajes, resultadoAnon = obtener_respuesta(textOri, historial_mensajes,
                                                              resultadoJSONAnnon)
    #print(f"Historial_mensajes: {historial_mensajes}")
    #print(f"Texto resultadoAnon: {resultadoAnon['message']['content']}")
    resultadoJSONAnnon2 = extract_json(resultadoAnon['message']['content'])
    return resultadoJSONAnnon2, resultadoAnon['message']['content']


def procesaResultado(diccionario_textOri, jsonInitialFindings):
    ResultadoSalida = []
    ResultadoErrores = []
    historial_mensajes = []
    for clave, textOri in diccionario_textOri.items():

        resultadoJSONAnnonUni, resultadoContent = intentoBase(textOri, historial_mensajes,
                                                              jsonInitialFindings)
        if resultadoJSONAnnonUni is None:

            resultadoJSONAnnonUni, resultadoContent = intentoBase(textOri, historial_mensajes,
                                                                  jsonInitialFindings)

            if resultadoJSONAnnonUni is None:

                resultadoJSONAnnonUni, resultadoContent = intentoBase(textOri, historial_mensajes,
                                                                      jsonInitialFindings)
                if resultadoJSONAnnonUni is None:
                    dictvalor = dict();
                    dictvalor["text"] = textOri
                    dictvalor["res"] = resultadoContent
                    ResultadoErrores.append(dictvalor)
                    print("not found", resultadoContent)

        if resultadoJSONAnnonUni is not None:
            dictvalor = dict();
            dictvalor["clave"] = clave
            dictvalor["texto"] = textOri
            dictvalor["anotado"] = resultadoJSONAnnonUni
            ResultadoSalida.append(dictvalor)
            print("Case", clave, "Result", resultadoJSONAnnonUni)

    return ResultadoSalida, ResultadoErrores

def salvarSalida(ResultadoSalida, ResultadoErrores, archivo_salida, archivo_salidaE):


    # Guardar el JSON en el archivo
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(ResultadoSalida, f, indent=4, ensure_ascii=False)

    print(f"JSON guardado en {archivo_salida}")


    # Guardar el JSON en el archivo
    with open(archivo_salidaE, "w", encoding="utf-8") as f:
        json.dump(ResultadoErrores, f, indent=4, ensure_ascii=False)

    print(f"JSON guardado en {archivo_salidaE}")


# Leer el archivo JSON desanonimizado
archivo_salida = "resultados_desanonimizados.json"
with open(archivo_salida, "r", encoding="utf-8") as f:
    datos = json.load(f)

# Crear las listas de textOri y textDesa
# Crear los dos diccionarios
diccionario_textOri = {item["clave"]: item["textOri"] for item in datos}
diccionario_textDesa = {item["clave"]: item["textDesa"] for item in datos}

# Imprimir los resultados
#print("Lista de textOri:", lista_textOri)
#print("Lista de textDesa:", lista_textDesa)



# Leer el archivo JSON etiquetas
archivo_salidaNormal = "resultadoFinalNormal.json"
with open(archivo_salidaNormal, "r", encoding="utf-8") as f:
    datos = json.load(f)


# Crear las listas de listaFindings
listaFindings = [objeto["finding"] for objeto in datos]

print("Recorriendo ORI:ORI:")

# Text ORIGINAL contra lista ORIGINAL
ResultadoSalidaNormalNormal,ResultadoErrores = procesaResultado(diccionario_textOri,listaFindings)


# Nombre del archivo donde se guardará el JSON
archivo_salida = "resultadoFinalNormalDocNN.json"

# Nombre del archivo donde se guardará el JSON
archivo_salidaE = "resultadoFinalNormalDocENN.json "

salvarSalida(ResultadoSalidaNormalNormal,ResultadoErrores,archivo_salida,archivo_salidaE)



print("Recorriendo DES:ORI:")

# Text DESAMBIGUADO contra lista ORIGINAL
ResultadoSalidaNormalNormal,ResultadoErrores = procesaResultado(diccionario_textDesa,listaFindings)


# Nombre del archivo donde se guardará el JSON
archivo_salida = "resultadoFinalNormalDocDN.json"

# Nombre del archivo donde se guardará el JSON
archivo_salidaE = "resultadoFinalNormalDocEDN.json "

salvarSalida(ResultadoSalidaNormalNormal,ResultadoErrores,archivo_salida,archivo_salidaE)


# Leer el archivo JSON etiquetas
archivo_salidaAnnon = "resultadoFinalAnnon.json"
with open(archivo_salidaAnnon, "r", encoding="utf-8") as f:
    datos = json.load(f)


# Crear las listas de listaFindings
listaFindings = [objeto["finding"] for objeto in datos]

print("Recorriendo ORI:DES:")
# Text ORIGINAL contra lista ORIGINAL
ResultadoSalidaNormalNormal,ResultadoErrores = procesaResultado(diccionario_textOri,listaFindings)


# Nombre del archivo donde se guardará el JSON
archivo_salida = "resultadoFinalNormalDocND.json"

# Nombre del archivo donde se guardará el JSON
archivo_salidaE = "resultadoFinalNormalDocEND.json "

salvarSalida(ResultadoSalidaNormalNormal,ResultadoErrores,archivo_salida,archivo_salidaE)




print("Recorriendo DES:DES:")
ResultadoSalidaNormalNormal,ResultadoErrores = procesaResultado(diccionario_textDesa,listaFindings)


# Nombre del archivo donde se guardará el JSON
archivo_salida = "resultadoFinalNormalDocDD.json"

# Nombre del archivo donde se guardará el JSON
archivo_salidaE = "resultadoFinalNormalDocEDD.json "

salvarSalida(ResultadoSalidaNormalNormal,ResultadoErrores,archivo_salida,archivo_salidaE)