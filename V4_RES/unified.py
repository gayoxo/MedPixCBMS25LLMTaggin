import os
import json


def unify_json_files(folder_path, output_filename):
    """
    Recorre una carpeta, lee todos los archivos JSON y unifica su contenido sin duplicar valores de "finding".

    :param folder_path: Ruta de la carpeta que contiene los archivos JSON.
    :param output_filename: Nombre del archivo JSON unificado de salida.
    """
    unique_findings = set()

    # Recorre todos los archivos en la carpeta
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):  # Solo archivos JSON
            file_path = os.path.join(folder_path, filename)

            # Leer el archivo JSON
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    # Agregar los findings al set (evita duplicados)
                    for item in data:
                        if "finding" in item:
                            unique_findings.add(item["finding"])
                except json.JSONDecodeError:
                    print(f"Error al leer {filename}, archivo JSON mal formado.")

    # Convertir el set en lista de diccionarios y ordenarlos alfabéticamente
    final_json = [{"finding": finding} for finding in sorted(unique_findings)]

    # Ruta del archivo de salida
    output_path = os.path.join(folder_path, output_filename)

    # Guardar en un nuevo archivo JSON
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(final_json, outfile, indent=4, ensure_ascii=False)

    print(f"Archivo JSON unificado guardado en: {output_path}")

# Ejemplo de uso:
unify_json_files("TagBag/NORMAL", "resultadoFinalNormal.json")
unify_json_files("TagBag/DESANNON", "resultadoFinalAnnon.json")