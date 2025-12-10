import json

def modify_notebook(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    # 1. Modify Configuration Cell (Cell 5 - Index 2 or 3 depending on markdown cells)
    # We look for the cell containing GITHUB_REPO
    
    config_cell_found = False
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if "GITHUB_REPO =" in source and "HF_DATASET_REPO =" in source:
                print("Found Config Cell. Modifying...")
                new_source = [
                    "# \ud83d\udd27 CONFIGURATION - Modifiez ces valeurs\n",
                    "GITHUB_REPO = \"Racim679/tts\"  # Votre repo GitHub\n",
                    "\n",
                    "print(f\"\u2705 GitHub: {GITHUB_REPO}\")"
                ]
                cell['source'] = new_source
                config_cell_found = True
                break
    
    if not config_cell_found:
        print("Warning: Config cell not found!")

    # 2. Modify Download Cell (Cell 9)
    # Looking for snapshot_download
    
    download_cell_found = False
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if "snapshot_download" in source and "drive.mount" in source:
                print("Found Download Cell. Modifying...")
                new_source = [
                    "import os\n",
                    "from google.colab import drive\n",
                    "\n",
                    "# Monter Google Drive si n\u00e9cessaire\n",
                    "if not os.path.exists('/content/drive'):\n",
                    "    drive.mount('/content/drive')\n",
                    "\n",
                    "# Cloner StyleTTS2\n",
                    "if not os.path.exists(\"/content/StyleTTS2\"):\n",
                    "    !git clone https://github.com/yl4579/StyleTTS2.git /content/StyleTTS2\n",
                    "    print(\"\u2705 StyleTTS2 clon\u00e9!\")\n",
                    "else:\n",
                    "    print(\"\u2139\ufe0f StyleTTS2 d\u00e9j\u00e0 pr\u00e9sent\")\n",
                    "\n",
                    "# Cloner votre repo avec les configs\n",
                    "if not os.path.exists(\"/content/arable-tts\"):\n",
                    "    !git clone https://github.com/{GITHUB_REPO}.git /content/arable-tts\n",
                    "    print(\"\u2705 Configs clon\u00e9es depuis GitHub!\")\n",
                    "else:\n",
                    "    print(\"\u2139\ufe0f Repo d\u00e9j\u00e0 pr\u00e9sent\")\n",
                    "\n",
                    "# \ud83d\udce5 LOGIQUE DE T\u00c9L\u00c9CHARGEMENT DES DONN\u00c9ES\n",
                    "# 1. V\u00e9rifier si le ZIP existe sur Drive\n",
                    "drive_zip_path = \"/content/drive/MyDrive/darija_dataset.zip\"\n",
                    "local_dataset_path = \"/content/dataset_darija\"\n",
                    "\n",
                    "if os.path.exists(drive_zip_path):\n",
                    "    print(f\"\ud83d\udce6 ZIP trouv\u00e9 sur Drive: {drive_zip_path}\")\n",
                    "    print(\"\u23f3 Extraction en cours... (\u00e7a peut prendre 1-2 min)\")\n",
                    "    !unzip -q {drive_zip_path} -d {local_dataset_path}\n",
                    "    print(\"\u2705 Donn\u00e9es extraites depuis Drive!\")\n",
                    "else:\n",
                    "    print(\"\u274c ZIP non trouv\u00e9 sur Drive! (darija_dataset.zip)\")\n",
                    "    print(\"\u26a0\ufe0f Veuillez uploader le fichier zip \u00e0 la racine de votre Drive.\")\n",
                    "\n",
                    "# V\u00e9rifier ce qui a \u00e9t\u00e9 t\u00e9l\u00e9charg\u00e9\n",
                    "if os.path.exists(f\"{local_dataset_path}/wavs\"):\n",
                    "    wav_count = len([f for f in os.listdir(f\"{local_dataset_path}/wavs\") if f.endswith('.wav')])\n",
                    "    print(f\"\ud83c\udfb5 {wav_count} fichiers audio d\u00e9tect\u00e9s\")\n",
                    "\n",
                    "metadata_files = [\"metadata_train.csv\", \"metadata_eval.csv\", \"metadata.json\"]\n",
                    "for mf in metadata_files:\n",
                    "    if os.path.exists(f\"{local_dataset_path}/{mf}\"):\n",
                    "        print(f\"\ud83d\udcc4 {mf} pr\u00e9sent\")"
                ]
                cell['source'] = new_source
                download_cell_found = True
                break

    if not download_cell_found:
        print("Warning: Download cell not found!")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1)
    
    print("Notebook modified successfully.")

if __name__ == "__main__":
    modify_notebook("COLAB_NOTEBOOK_FINAL.ipynb")
