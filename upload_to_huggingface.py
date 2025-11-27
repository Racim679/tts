"""
Script pour uploader le dataset audio sur Hugging Face
Ce script upload les fichiers audio et les métadonnées sur un dataset Hugging Face
"""

import os
import sys
from huggingface_hub import HfApi, login
from pathlib import Path
import argparse

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def upload_dataset_to_hf(hf_token, repo_name, dataset_path):
    """
    Upload le dataset sur Hugging Face

    Args:
        hf_token: Token d'accès Hugging Face
        repo_name: Nom du repo (format: username/dataset-name)
        dataset_path: Chemin vers le dossier dataset_training
    """
    # Login à Hugging Face
    print("🔐 Connexion à Hugging Face...")
    login(token=hf_token)

    api = HfApi()

    # Créer le dataset s'il n'existe pas
    try:
        print(f"📦 Création/Vérification du dataset {repo_name}...")
        api.create_repo(
            repo_id=repo_name,
            repo_type="dataset",
            exist_ok=True
        )
        print(f"✅ Dataset {repo_name} prêt!")
    except Exception as e:
        print(f"⚠️ Avertissement lors de la création du repo: {e}")

    dataset_path = Path(dataset_path)

    # Upload les fichiers audio
    wavs_path = dataset_path / "wavs"
    if wavs_path.exists():
        print(f"🎵 Upload des fichiers audio depuis {wavs_path}...")
        print(f"   Nombre de fichiers: {len(list(wavs_path.glob('*.wav')))}")

        api.upload_folder(
            folder_path=str(wavs_path),
            path_in_repo="wavs",
            repo_id=repo_name,
            repo_type="dataset"
        )
        print("✅ Fichiers audio uploadés!")
    else:
        print(f"⚠️ Dossier {wavs_path} introuvable!")

    # Upload les fichiers de métadonnées
    metadata_files = [
        "metadata_train.csv",
        "metadata_eval.csv",
        "metadata.json"
    ]

    print("📄 Upload des métadonnées...")
    for metadata_file in metadata_files:
        metadata_path = dataset_path / metadata_file
        if metadata_path.exists():
            print(f"   • {metadata_file}")
            api.upload_file(
                path_or_fileobj=str(metadata_path),
                path_in_repo=metadata_file,
                repo_id=repo_name,
                repo_type="dataset"
            )

    print("\n🎉 Upload terminé avec succès!")
    print(f"🔗 Dataset disponible sur: https://huggingface.co/datasets/{repo_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload dataset audio sur Hugging Face")
    parser.add_argument("--token", type=str, help="Token Hugging Face (ou utilisez HF_TOKEN env variable)")
    parser.add_argument("--repo", type=str, required=True, help="Nom du repo (username/dataset-name)")
    parser.add_argument("--dataset-path", type=str, default="dataset_training", help="Chemin vers dataset_training")

    args = parser.parse_args()

    # Récupérer le token depuis les arguments ou variable d'environnement
    hf_token = args.token or os.getenv("HF_TOKEN")

    if not hf_token:
        print("❌ Erreur: Token Hugging Face manquant!")
        print("   Utilisez --token YOUR_TOKEN ou définissez HF_TOKEN")
        exit(1)

    upload_dataset_to_hf(hf_token, args.repo, args.dataset_path)
