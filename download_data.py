import os
import shutil
from huggingface_hub import snapshot_download

HF_DATASET_REPO = "RacimPoly6/darija-tts-dataset"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset_training")
STYLETTS2_WAVS = os.path.join(BASE_DIR, "StyleTTS2", "wavs")

def main():
    print(f"Downloading dataset {HF_DATASET_REPO}...")
    try:
        snapshot_download(
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            local_dir=DATASET_DIR,
            local_dir_use_symlinks=False
        )
        print("Dataset downloaded successfully.")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return

    # Copy wavs to StyleTTS2/wavs
    source_wavs = os.path.join(DATASET_DIR, "wavs")
    if os.path.exists(source_wavs):
        print(f"Copying wavs from {source_wavs} to {STYLETTS2_WAVS}...")
        os.makedirs(STYLETTS2_WAVS, exist_ok=True)
        
        wav_files = [f for f in os.listdir(source_wavs) if f.endswith('.wav')]
        print(f"Found {len(wav_files)} wav files.")
        
        for f in wav_files:
            shutil.copy2(os.path.join(source_wavs, f), os.path.join(STYLETTS2_WAVS, f))
        print("Copy complete.")
    else:
        print(f"Warning: {source_wavs} not found after download.")

if __name__ == "__main__":
    main()
