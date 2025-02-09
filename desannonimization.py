import json
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
        "Return only the modified report without any explanations or additional text."
        "Do not change the statements, only replace XXX if apear with the replacement\n\n"
    )

    # Enviar la solicitud al modelo
    response = client.chat(model='deepseek-r1', messages=[
        {
            'role': 'user',
            'content': content_text,
        },
    ])

    print(texto_anonimizado)
    print(response)

    if response:
        return response['message']['content']
    else:
        print("Error al obtener respuesta del modelo.")
        return None


# Leer el archivo JSON
archivo_resultado = "resultados.json"
with open(archivo_resultado, "r", encoding="utf-8") as f:
    datos = json.load(f)

# Crear una nueva estructura para el JSON resultante
nueva_estructura = []
for etiqueta, texto in datos.items():
    nuevo_objeto = {
        "clave": etiqueta,
        "textOri": texto,
        "textDesa": desanonimizar_informe_medico(texto)
    }
    nueva_estructura.append(nuevo_objeto)

# Guardar la nueva estructura en un archivo JSON
archivo_salida = "resultados_desanonimizados.json"
with open(archivo_salida, "w", encoding="utf-8") as f:
    json.dump(nueva_estructura, f, indent=4, ensure_ascii=False)

print(f"Nuevo JSON generado en {archivo_salida}")