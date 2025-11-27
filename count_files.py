import json
from pathlib import Path

metadata = json.load(open('dataset_training/metadata.json', 'r', encoding='utf-8'))
wav_dir = Path('dataset_training/wavs')
all_wavs = set(f.name for f in wav_dir.glob('*.wav'))
in_metadata = set(item['audio_file'].replace('wavs/', '') for item in metadata)
missing = all_wavs - in_metadata

print(f'Total fichiers WAV dans wavs/: {len(all_wavs)}')
print(f'Fichiers dans metadata.json: {len(in_metadata)}')
print(f'Fichiers manquants dans metadata.json: {len(missing)}')
print(f'\nPremiers fichiers manquants:')
for f in sorted(missing)[:20]:
    print(f'  - {f}')

