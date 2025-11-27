"""
Script pour télécharger le dataset depuis Hugging Face
À utiliser dans Google Colab ou en local
"""

import os
from huggingface_hub import snapshot_download
from pathlib import Path
import argparse

def download_dataset_from_hf(repo_name, output_dir="dataset_training", hf_token=None):
    """
    Télécharge le dataset depuis Hugging Face

    Args:
        repo_name: Nom du repo (format: username/dataset-name)
        output_dir: Dossier de destination
        hf_token: Token Hugging Face (optionnel pour datasets publics)
    """
    print(f"📥 Téléchargement du dataset depuis {repo_name}...")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        # Télécharger tout le dataset
        local_dir = snapshot_download(
            repo_id=repo_name,
            repo_type="dataset",
            local_dir=str(output_path),
            token=hf_token
        )

        print(f"✅ Dataset téléchargé dans: {local_dir}")

        # Vérifier les fichiers
        wavs_path = output_path / "wavs"
        if wavs_path.exists():
            wav_count = len(list(wavs_path.glob("*.wav")))
            print(f"🎵 {wav_count} fichiers audio trouvés")

        metadata_files = ["metadata_train.csv", "metadata_eval.csv", "metadata.json"]
        for metadata_file in metadata_files:
            if (output_path / metadata_file).exists():
                print(f"📄 {metadata_file} téléchargé")

        print("\n🎉 Téléchargement terminé avec succès!")
        return str(local_dir)

    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        raise

def setup_colab_environment(repo_name, hf_token=None):
    """
    Configure l'environnement Colab avec le dataset
    """
    print("🔧 Configuration de l'environnement Colab...")

    # Installer les dépendances si nécessaire
    try:
        import huggingface_hub
    except ImportError:
        print("📦 Installation de huggingface_hub...")
        os.system("pip install -q huggingface_hub")

    # Télécharger le dataset
    dataset_path = download_dataset_from_hf(repo_name, "dataset_training", hf_token)

    print(f"\n✅ Environnement prêt!")
    print(f"📁 Dataset disponible dans: {dataset_path}")

    return dataset_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Télécharger dataset depuis Hugging Face")
    parser.add_argument("--repo", type=str, required=True, help="Nom du repo (username/dataset-name)")
    parser.add_argument("--output", type=str, default="dataset_training", help="Dossier de sortie")
    parser.add_argument("--token", type=str, help="Token Hugging Face (pour datasets privés)")

    args = parser.parse_args()

    hf_token = args.token or os.getenv("HF_TOKEN")

    download_dataset_from_hf(args.repo, args.output, hf_token)
