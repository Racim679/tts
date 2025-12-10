import os
import soundfile as sf
import glob
from concurrent.futures import ProcessPoolExecutor
import tqdm

wav_dir = r"c:\Users\Racim\Desktop\arable tts\StyleTTS2\wavs"
wav_files = glob.glob(os.path.join(wav_dir, "*.wav"))

print(f"Found {len(wav_files)} wav files in {wav_dir}")

def check_file(wav_path):
    try:
        data, sr = sf.read(wav_path)
        return None
    except Exception as e:
        return f"Failed to read {wav_path}: {e}"

if __name__ == "__main__":
    print("Testing file reading with multiprocessing...")
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(tqdm.tqdm(executor.map(check_file, wav_files), total=len(wav_files)))
    
    failures = [r for r in results if r is not None]
    if failures:
        print(f"Found {len(failures)} failures:")
        for f in failures[:10]:
            print(f)
    else:
        print("All files read successfully.")
