import os
import xml.etree.ElementTree as ET
import json

def extraer_datos_de_xml(ruta_archivo):
    try:
        # Parsear el archivo XML
        tree = ET.parse(ruta_archivo)
        root = tree.getroot()

        # Obtener el nombre de la primera etiqueta (el nodo raíz)
        etiqueta_principal = root.tag

        # Obtener el contenido de la etiqueta <Texto>
        texto = root.find("Texto").text if root.find("Texto") is not None else None

        return etiqueta_principal, texto
    except Exception as e:
        print(f"Error procesando el archivo {ruta_archivo}: {e}")
        return None, None


# Recorrer una carpeta y procesar los archivos XML
def procesar_carpetas_xml(directorio):
    resultados = {}
    for archivo in os.listdir(directorio):
        if archivo.endswith(".xml"):
            ruta_archivo = os.path.join(directorio, archivo)
            etiqueta, texto = extraer_datos_de_xml(ruta_archivo)
            if etiqueta and texto:
                resultados[archivo] = {"Etiqueta": etiqueta, "Texto": texto}
    return resultados


# Ejemplo de uso
directorio = "Documentos"  # Cambia esto por tu directorio
resultados = procesar_carpetas_xml(directorio)

print("Datos extraídos de los archivos XML:")
for archivo, datos in resultados.items():
    print(f"Archivo: {archivo}")
    print(f"Etiqueta Principal: {datos['Etiqueta']}")
    print(f"Texto: {datos['Texto']}")
    print()



# Reestructurar los resultados para que solo incluyan la etiqueta y el texto
resultados_reestructurados = {datos["Etiqueta"]: datos["Texto"] for datos in resultados.values()}

# Guardar resultados en un archivo JSON
archivo_resultado = "datacleanOld.json"
with open(archivo_resultado, "w", encoding="utf-8") as f:
    json.dump(resultados_reestructurados, f, indent=4, ensure_ascii=False)

print(f"Resultados guardados en el archivo {archivo_resultado}")