import os
import shutil
import subprocess
import requests
import yaml
import json
import random
import re
import sys
import time

# Configuration
GITHUB_REPO = "Racim679/tts"
HF_DATASET_REPO = "RacimPoly6/darija-tts-dataset"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLETTS2_DIR = os.path.join(BASE_DIR, "StyleTTS2")
DATASET_DIR = os.path.join(BASE_DIR, "dataset_training") # Assuming this is where local data is
AUDIO_DIR = os.path.join(DATASET_DIR, "wavs") # Adjust if structure is different
METADATA_FILE = os.path.join(DATASET_DIR, "metadata.json")

def run_command(command, cwd=None):
    print(f"Running: {command}")
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def download_file(url, dest_path):
    print(f"Downloading {url} to {dest_path}...")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    try:
        # Use curl.exe for better reliability and speed on Windows
        subprocess.check_call(["curl.exe", "-L", "-o", dest_path, url])
        print("Done.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {url}: {e}")
        # Fallback to requests if curl fails
        try:
            print("Retrying with requests...")
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Done.")
        except Exception as e2:
            print(f"Failed to download {url} with requests: {e2}")

def setup_styletts2():
    if not os.path.exists(STYLETTS2_DIR):
        print("Cloning StyleTTS2...")
        run_command(f"git clone https://github.com/yl4579/StyleTTS2.git \"{STYLETTS2_DIR}\"")
    else:
        print("StyleTTS2 already exists.")

    # Create directories
    dirs = [
        "Models/LibriTTS", "Models/Darija",
        "Utils/JDC", "Utils/ASR", "Utils/PLBERT",
        "Data", "wavs", "Configs"
    ]
    for d in dirs:
        os.makedirs(os.path.join(STYLETTS2_DIR, d), exist_ok=True)

def download_models():
    downloads = [
        ("Models/LibriTTS/epochs_2nd_00020.pth", "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/Models/LibriTTS/epochs_2nd_00020.pth"),
        ("Models/LibriTTS/config.yml", "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/Models/LibriTTS/config.yml"),
        ("Utils/JDC/bst.t7", "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/Utils/JDC/bst.t7"),
        ("Utils/ASR/epoch_00080.pth", "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/Utils/ASR/epoch_00080.pth"),
        ("Utils/ASR/config.yml", "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/Utils/ASR/config.yml"),
        ("Utils/PLBERT/step_1000000.t7", "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/Utils/PLBERT/step_1000000.t7"),
        ("Utils/PLBERT/config.yml", "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/Utils/PLBERT/config.yml"),
    ]

    for path, url in downloads:
        dest = os.path.join(STYLETTS2_DIR, path)
        if not os.path.exists(dest) or os.path.getsize(dest) == 0:
            download_file(url, dest)
        else:
            print(f"Skipping {path}, already exists.")

def patch_files():
    files_to_patch = [
        "models.py",
        "Utils/ASR/models.py",
        "Utils/JDC/model.py",
        "Utils/PLBERT/util.py",
        "meldataset.py",
    ]
    
    print("Patching files for PyTorch weights_only issue...")
    for rel_path in files_to_patch:
        filepath = os.path.join(STYLETTS2_DIR, rel_path)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'torch.load' in content and 'weights_only' not in content:
                new_content = re.sub(r'torch\.load\(([^)]+)\)', r'torch.load(\1, weights_only=False)', content)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Patched {rel_path}")
            else:
                print(f"Already patched or not needed: {rel_path}")

def prepare_data():
    print("Preparing data...")
    
    # Copy wavs
    dest_wavs = os.path.join(STYLETTS2_DIR, "wavs")
    if os.path.exists(AUDIO_DIR):
        wav_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith('.wav')]
        print(f"Found {len(wav_files)} wav files in {AUDIO_DIR}")
        for f in wav_files:
            shutil.copy2(os.path.join(AUDIO_DIR, f), os.path.join(dest_wavs, f))
    else:
        print(f"WARNING: Audio directory {AUDIO_DIR} not found. Please ensure your audio files are there.")

    # Create train/val lists
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Filter out entries where audio file doesn't exist
        valid_metadata = []
        for item in metadata:
            # Extract just the filename (remove wavs/ prefix if present)
        random.seed(42)
        random.shuffle(valid_metadata)
        split = int(len(valid_metadata) * 0.95)
        train_data, eval_data = valid_metadata[:split], valid_metadata[split:]

        with open(os.path.join(STYLETTS2_DIR, "Data/train_list.txt"), 'w', encoding='utf-8') as f:
            for item in train_data:
                f.write(f"{item['audio_file']}|{item['text'].replace(chr(10), ' ')}|0\n")
        
        with open(os.path.join(STYLETTS2_DIR, "Data/val_list.txt"), 'w', encoding='utf-8') as f:
            for item in eval_data:
                f.write(f"{item['audio_file']}|{item['text'].replace(chr(10), ' ')}|0\n")
        
        print(f"Created train_list.txt ({len(train_data)}) and val_list.txt ({len(eval_data)})")
    else:
        print(f"WARNING: Metadata file {METADATA_FILE} not found.")

def create_config():
    print("Creating configuration...")
            'val_data': 'Data/val_list.txt',
            'root_path': '',
            'OOD_data': 'Data/OOD_texts.txt',
            'min_length': 50,
            'sample_rate': 24000,
        },
        'preprocess_params': {
            'sr': 24000,
            'spect_params': {
                'n_fft': 2048,
                'win_length': 1200,
                'hop_length': 300,
                'n_mels': 80
            }
        },
        'model_params': {
            'multispeaker': True,
            'dim_in': 64,
            'hidden_dim': 512,
            'max_conv_dim': 512,
            'n_layer': 3,
            'n_mels': 80,
            'n_token': 178,
            'max_dur': 50,
            'style_dim': 128,
            'dropout': 0.2,
            'decoder': {
                'type': 'hifigan',
                'resblock_kernel_sizes': [3, 7, 11],
                'upsample_rates': [10, 5, 3, 2],
                'upsample_initial_channel': 512,
                'resblock_dilation_sizes': [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
                'upsample_kernel_sizes': [20, 10, 6, 4],
            },
            'slm': {
                'model': 'microsoft/wavlm-base-plus',
                'sr': 16000,
                'hidden': 768,
                'nlayers': 13,
                'initial_channel': 64
            },
            'diffusion': {
                'embedding_mask_proba': 0.1,
                'transformer': {
                    'num_layers': 3,
                    'num_heads': 8,
                    'head_features': 64,
                    'multiplier': 2
                },
                'dist': {
                    'sigma_data': 0.2,
                    'estimate_sigma_data': True,
                    'mean': -3.0,
                    'std': 1.0
                }
            }
        },
        'loss_params': {
            'lambda_mel': 5.0,
            'lambda_gen': 1.0,
            'lambda_slm': 1.0,
            'lambda_mono': 1.0,
            'lambda_s2s': 1.0,
            'lambda_F0': 1.0,
            'lambda_norm': 1.0,
            'lambda_dur': 1.0,
            'lambda_ce': 20.0,
            'lambda_sty': 1.0,
            'lambda_diff': 1.0,
            'diff_epoch': 20,
            'joint_epoch': 40
        },
        'optimizer_params': {
            'lr': 0.0001,
            'bert_lr': 1e-5,
            'ft_lr': 1e-4
        },
        'slmadv_params': {
            'min_len': 400,
            'max_len': 500,
            'batch_percentage': 0.5,
            'iter': 10,
            'thresh': 5.0,
            'scale': 0.01,
            'sig': 1.5
        },
        'F0_path': 'Utils/JDC/bst.t7',
        'ASR_config': 'Utils/ASR/config.yml',
        'ASR_path': 'Utils/ASR/epoch_00080.pth',
        'PLBERT_dir': 'Utils/PLBERT/',
    }

    with open(os.path.join(STYLETTS2_DIR, 'Configs/config_darija_ft.yml'), 'w') as f:
        yaml.dump(config, f)
    
    # Create OOD_texts.txt (dummy)
    with open(os.path.join(STYLETTS2_DIR, 'Data/OOD_texts.txt'), 'w') as f:
        f.write("This is a dummy out of distribution text.\n")

def main():
    setup_styletts2()
    download_models()
    patch_files()
    prepare_data()
    create_config()
    print("\nSetup complete! You can now run 'python train_local.py'")

if __name__ == "__main__":
    main()
