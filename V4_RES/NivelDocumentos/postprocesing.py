import json

def generarPreprocesado(archivo_json, archivo_json_preprocesed):
    # Leer el archivo JSON
    with open(archivo_json, "r", encoding="utf-8") as f:
        datos = json.load(f)  # Cargar el JSON como lista de diccionarios

    # Lista para almacenar la nueva estructura filtrada
    nuevo_json = []

    # Recorrer cada entrada del JSON y filtrar los términos presentes
    for entrada in datos:
        anotado = entrada.get("anotado", [])  # Si no existe, poner una lista vacía

        # Si "anotado" es una cadena JSON mal formateada, intentar convertirla a lista
        if isinstance(anotado, str):
            try:
                anotado = json.loads(anotado)  # Intenta cargarlo como JSON
            except json.JSONDecodeError:
                anotado = []

        # Si "anotado" es un diccionario, convertirlo en una lista de findings
        if isinstance(anotado, dict):
            anotado = [{"finding": key, "absent": not value} for key, value in anotado.items()]

        try:
            # Si "anotado" es una lista de diccionarios, filtramos los findings presentes
            if isinstance(anotado, list) and all(isinstance(item, dict) for item in anotado):
                findings_presentes = [
                    item["finding"]
                    for item in anotado
                    if not item.get("absent", False)  # Si "absent" no está presente, asumimos que es False
                ]


            # Si "anotado" es una lista de strings, la usamos directamente
            elif isinstance(anotado, list) and all(isinstance(item, str) for item in anotado):
                findings_presentes = anotado  # Ya es la lista correcta

            # Si "anotado" es de un tipo inesperado, lo dejamos vacío
            else:
                findings_presentes = []

        except KeyError:
            print("Inesperado:","Archivo:",archivo_json,"//Entrada", entrada["clave"],anotado)
            findings_presentes = []

        # Crear la nueva estructura con la clave, texto y findings unidos en una lista de strings
        nuevo_documento = {
            "clave": entrada["clave"],
            "texto": entrada["texto"],
            "anotado": findings_presentes
        }

        # Agregar al nuevo JSON
        nuevo_json.append(nuevo_documento)


    # Guardar el resultado en un nuevo archivo
    with open(archivo_json_preprocesed, "w", encoding="utf-8") as f:
        json.dump(nuevo_json, f, indent=4, ensure_ascii=False)

    # Imprimir el resultado en pantalla
    #print(json.dumps(nuevo_json, indent=4, ensure_ascii=False))

archivo_json = "resultadoFinalNormalDocDD.json"
archivo_json_preprocesed = "resultadoFinalNormalDocDD__PP.json"

generarPreprocesado(archivo_json,archivo_json_preprocesed)

archivo_json = "resultadoFinalNormalDocND.json"
archivo_json_preprocesed = "resultadoFinalNormalDocND__PP.json"

generarPreprocesado(archivo_json,archivo_json_preprocesed)

archivo_json = "resultadoFinalNormalDocDN.json"
archivo_json_preprocesed = "resultadoFinalNormalDocDN__PP.json"

generarPreprocesado(archivo_json,archivo_json_preprocesed)

archivo_json = "resultadoFinalNormalDocNN.json"
archivo_json_preprocesed = "resultadoFinalNormalDocNN__PP.json"

generarPreprocesado(archivo_json,archivo_json_preprocesed)



