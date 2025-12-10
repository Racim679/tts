import json

notebook_path = "COLAB_NOTEBOOK_FINAL.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

new_cells = []
deleted_count = 0

for cell in nb["cells"]:
    # 1. Modify the Git Clone cell
    if cell["cell_type"] == "code" and "git clone" in "".join(cell["source"]):
        # Check if it's the main download cell
        if "StyleTTS2.git" in "".join(cell["source"]) and "3. T" in "".join(cell.get("source", [])) or "3. " in "".join([c["source"][0] if c.get("source") else "" for c in nb["cells"] if c["cell_type"] == "markdown" and c == cell]): 
             # It's hard to match by markdown header from here, so looking at content
             pass
        
        # Let's match by content more robustly
        source_text = "".join(cell["source"])
        if "Cloner StyleTTS2" in source_text and "Cloner votre repo" in source_text:
            print("Found Git Clone cell. Updating...")
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
                "# 📥 DONNÉES (Dataset)\n",
                "drive_zip_path = \"/content/drive/MyDrive/darija_dataset.zip\"\n",
                "local_dataset_path = \"/content/darija_dataset\"\n",
                "\n",
                "if os.path.exists(drive_zip_path):\n",
                "    print(f\"📦 ZIP trouvé: {drive_zip_path}\")\n",
                "    if not os.path.exists(local_dataset_path):\n",
                "        print(\"⏳ Extraction...\")\n",
                "        !unzip -q {drive_zip_path} -d {local_dataset_path}\n",
                "        print(\"✅ Données extraites !\")\n",
                "    else:\n",
                "        print(\"ℹ️ Données déjà extraites\")\n",
                "else:\n",
                "    print(\"⚠️ ZIP 'darija_dataset.zip' introuvable sur Drive !\")\n"
            ]
            new_cells.append(cell)
            continue

    # 2. Remove the "Copy Optimized Files" cell
    if cell["cell_type"] == "code" and "COPY OPTIMIZED FILES" in "".join(cell["source"]):
        print("Removing redundant 'COPY OPTIMIZED FILES' cell.")
        deleted_count += 1
        continue
    
    # Keep other cells
    new_cells.append(cell)

nb["cells"] = new_cells

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print(f"Notebook updated. Deleted {deleted_count} cells.")
