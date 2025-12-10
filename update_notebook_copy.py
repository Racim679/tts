import json

file_path = r'c:\Users\Racim\Desktop\arable tts - Copie\COLAB_NOTEBOOK_FINAL.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the cell where we clone the repo
clone_cell_index = -1
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and 'git clone' in ''.join(cell['source']):
        clone_cell_index = i
        break

if clone_cell_index != -1:
    # Create a new cell to copy the files
    copy_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 📂 COPY OPTIMIZED FILES FROM YOUR REPO TO STYLETTS2\n",
            "import shutil\n",
            "import os\n",
            "\n",
            "print(\"🔄 Mise à jour des fichiers avec la version A100...\")\n",
            "\n",
            "# Copy optimized training script\n",
            "shutil.copy(\"/content/arable-tts/train_finetune_optimized.py\", \"/content/StyleTTS2/train_finetune.py\")\n",
            "print(\"✅ Script d'entraînement mis à jour (AMP + TF32)\")\n",
            "\n",
            "# Copy A100 config\n",
            "os.makedirs(\"/content/StyleTTS2/Configs\", exist_ok=True)\n",
            "shutil.copy(\"/content/arable-tts/config_darija_a100.yml\", \"/content/StyleTTS2/Configs/config_darija_a100.yml\")\n",
            "print(\"✅ Config A100 copiée\")\n"
        ]
    }
    
    # Insert after the clone cell
    nb['cells'].insert(clone_cell_index + 1, copy_cell)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f)
    print("Notebook updated with copy commands.")
else:
    print("Could not find the clone cell.")
