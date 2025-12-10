import json

file_path = r'c:\Users\Racim\Desktop\arable tts - Copie\COLAB_NOTEBOOK_FINAL.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

modified = False

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            if 'HF_TOKEN =' in line and 'hf_' in line:
                line = 'HF_TOKEN = ""  # Optionnel, seulement si dataset privé\n'
                modified = True
            new_source.append(line)
        cell['source'] = new_source

if modified:
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f)
    print("Token removed from notebook.")
else:
    print("No token found or already removed.")
