import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLETTS2_DIR = os.path.join(BASE_DIR, "StyleTTS2")
CONFIG_PATH = os.path.join(STYLETTS2_DIR, "Configs/config_darija_ft.yml")

def main():
    if not os.path.exists(STYLETTS2_DIR):
        print("Error: StyleTTS2 directory not found. Please run 'python setup_local.py' first.")
        sys.exit(1)
    
    if not os.path.exists(CONFIG_PATH):
        print("Error: Config file not found. Please run 'python setup_local.py' first.")
        sys.exit(1)

    print("Starting training...")
    print(f"Config: {CONFIG_PATH}")
    
    # Change directory to StyleTTS2 to ensure relative imports work as expected in their code
    os.chdir(STYLETTS2_DIR)
    
    cmd = [
        sys.executable,
        "train_finetune.py",
        "--config_path", "./Configs/config_darija_ft.yml"
    ]
    
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"Training failed with error code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
