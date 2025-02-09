import json

# Ruta del archivo JSON
json_path = 'resultV1prepro.json'

# Leer el archivo JSON
with open(json_path, mode='r', encoding='utf-8') as file:
    data = json.load(file)

# Mostrar el contenido del JSON
for entry in data:
    print(f"Original: {entry['ori']}")
    print(f"Description: {entry['des']}")
    print("-" * 80)
