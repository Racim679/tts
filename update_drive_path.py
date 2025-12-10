import json

notebook_path = "COLAB_NOTEBOOK_FINAL.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source_text = "".join(cell["source"])
        # Update the download cell to include the 'arable_tts' folder check
        if "drive_zip_path =" in source_text and "darija_dataset.zip" in source_text:
            print("Found Data Load cell. Updating paths...")
            cell["source"] = [
                "import os\n",
                "from google.colab import drive\n",
                "\n",
                "# Monter Google Drive si nécessaire\n",
                "if not os.path.exists('/content/drive'):\n",
                "    drive.mount('/content/drive')\n",
                "\n",
                "# 🚀 CLONAGE DU PROJET (Source Unique: Racim679/tts)\n",
                "if not os.path.exists(\"/content/StyleTTS2\"):\n",
                "    print(\"🔄 Installation du code depuis Racim679/tts...\")\n",
                "    # On clone le repo principal dans un dossier temp\n",
                "    !git clone https://github.com/Racim679/tts.git /content/temp_repo\n",
                "    \n",
                "    # On déplace le dossier StyleTTS2 (le code) à la racine de Colab\n",
                "    # C'est ce dossier qui contient tout le code unifié\n",
                "    !mv /content/temp_repo/StyleTTS2 /content/StyleTTS2\n",
                "    \n",
                "    # Nettoyage\n",
                "    !rm -rf /content/temp_repo\n",
                "    print(\"✅ Code installé avec succès !\")\n",
                "else:\n",
                "    print(\"ℹ️ Code déjà présent\")\n",
                "\n",
                "# 📥 DONNÉES (Dataset depuis Drive)\n",
                "# Le user a précisé que le zip est dans le dossier 'arable_tts'\n",
                "possible_paths = [\n",
                "    \"/content/drive/MyDrive/arable_tts/darija_dataset.zip\", # Priorité 1\n",
                "    \"/content/drive/MyDrive/darija_dataset.zip\"           # Fallback racine\n",
                "]\n",
                "\n",
                "drive_zip_path = None\n",
                "for path in possible_paths:\n",
                "    if os.path.exists(path):\n",
                "        drive_zip_path = path\n",
                "        break\n",
                "\n",
                "local_dataset_path = \"/content/darija_dataset\"\n",
                "\n",
                "if drive_zip_path:\n",
                "    print(f\"📦 ZIP trouvé: {drive_zip_path}\")\n",
                "    if not os.path.exists(local_dataset_path):\n",
                "        print(\"⏳ Extraction...\")\n",
                "        !unzip -q {drive_zip_path} -d {local_dataset_path}\n",
                "        print(\"✅ Données extraites !\")\n",
                "    else:\n",
                "        print(\"ℹ️ Données déjà extraites\")\n",
                "else:\n",
                "    print(\"⚠️ ERREUR CRITIQUE : Fichier 'darija_dataset.zip' introuvable !\")\n",
                "    print(f\"❌ J'ai cherché ici : {possible_paths}\")\n",
                "    print(\"👉 Veuillez vérifier que le fichier est bien dans 'arable_tts' sur votre Drive.\")\n"
            ]

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("Notebook updated with correct Drive paths.")
