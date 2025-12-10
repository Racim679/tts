import json
import os

notebook_path = r"c:\Users\Racim\Desktop\arable tts - Copie\COLAB_NOTEBOOK_FINAL.ipynb"

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# New content for the data download cell
new_download_source = [
    "import os\n",
    "from huggingface_hub import snapshot_download\n",
    "from google.colab import drive\n",
    "\n",
    "# Monter Google Drive si nécessaire\n",
    "if not os.path.exists('/content/drive'):\n",
    "    drive.mount('/content/drive')\n",
    "\n",
    "# Cloner StyleTTS2\n",
    "if not os.path.exists(\"/content/StyleTTS2\"):\n",
    "    !git clone https://github.com/yl4579/StyleTTS2.git /content/StyleTTS2\n",
    "    print(\"✅ StyleTTS2 cloné!\")\n",
    "else:\n",
    "    print(\"ℹ️ StyleTTS2 déjà présent\")\n",
    "\n",
    "# Cloner votre repo avec les configs\n",
    "if not os.path.exists(\"/content/arable-tts\"):\n",
    "    !git clone https://github.com/{GITHUB_REPO}.git /content/arable-tts\n",
    "    print(\"✅ Configs clonées depuis GitHub!\")\n",
    "else:\n",
    "    print(\"ℹ️ Repo déjà présent\")\n",
    "\n",
    "# 📥 LOGIQUE DE TÉLÉCHARGEMENT DES DONNÉES\n",
    "# 1. Vérifier si le ZIP existe sur Drive\n",
    "drive_zip_path = \"/content/drive/MyDrive/darija_dataset.zip\"\n",
    "local_dataset_path = \"/content/dataset_darija\"\n",
    "\n",
    "if os.path.exists(drive_zip_path):\n",
    "    print(f\"📦 ZIP trouvé sur Drive: {drive_zip_path}\")\n",
    "    print(\"⏳ Extraction en cours... (ça peut prendre 1-2 min)\")\n",
    "    !unzip -q {drive_zip_path} -d {local_dataset_path}\n",
    "    print(\"✅ Données extraites depuis Drive!\")\n",
    "else:\n",
    "    print(\"⚠️ ZIP non trouvé sur Drive, tentative HuggingFace...\")\n",
    "    # Télécharger les audio depuis HuggingFace\n",
    "    print(f\"📥 Téléchargement audio depuis HuggingFace: {HF_DATASET_REPO}...\")\n",
    "    try:\n",
    "        snapshot_download(\n",
    "            repo_id=HF_DATASET_REPO,\n",
    "            repo_type=\"dataset\",\n",
    "            local_dir=local_dataset_path,\n",
    "            local_dir_use_symlinks=False,\n",
    "            token=HF_TOKEN if HF_TOKEN else None\n",
    "        )\n",
    "        print(\"✅ Dataset audio téléchargé depuis HuggingFace!\")\n",
    "    except Exception as e:\n",
    "        print(f\"❌ Erreur HuggingFace: {e}\")\n",
    "        print(\"💡 CONSEIL: Uploadez 'darija_dataset.zip' sur votre Google Drive pour éviter ça.\")\n",
    "\n",
    "# Vérifier ce qui a été téléchargé\n",
    "if os.path.exists(f\"{local_dataset_path}/wavs\"):\n",
    "    wav_count = len([f for f in os.listdir(f\"{local_dataset_path}/wavs\") if f.endswith('.wav')])\n",
    "    print(f\"🎵 {wav_count} fichiers audio détectés\")\n",
    "\n",
    "metadata_files = [\"metadata_train.csv\", \"metadata_eval.csv\", \"metadata.json\"]\n",
    "for mf in metadata_files:\n",
    "    if os.path.exists(f\"{local_dataset_path}/{mf}\"):\n",
    "        print(f\"📄 {mf} présent\")"
]

# Modify cells
modified_download = False
modified_copy = False

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source_str = "".join(cell['source'])
        
        # Modify download cell
        if "snapshot_download" in source_str and "Cloner StyleTTS2" in source_str:
            cell['source'] = new_download_source
            modified_download = True
            print("✅ Modified download cell")
            
        # Modify copy cell
        if "train_finetune_optimized.py" in source_str:
            new_source = []
            for line in cell['source']:
                new_source.append(line.replace("train_finetune_optimized.py", "train_finetune.py"))
            cell['source'] = new_source
            modified_copy = True
            print("✅ Modified copy cell")

if modified_download and modified_copy:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("🎉 Notebook successfully updated!")
else:
    print(f"⚠️ Warning: Download modified: {modified_download}, Copy modified: {modified_copy}")
