# Session de Troubleshooting - Fine-tuning StyleTTS2 Darija
**Date**: 2025-12-10
**Durée**: ~3 heures
**Statut Final**: ✅ Prêt pour training sur A100

---

## 📋 Résumé de la Session

### Problèmes Résolus

1. **Erreur `weights_only` dans PyTorch 2.6+**
   - **Cause**: PyTorch 2.6+ nécessite `weights_only=False` pour `torch.load()`
   - **Fichiers corrigés**:
     - `Utils/PLBERT/util.py:30`
     - `models.py` (plusieurs occurrences)
   - **Solution**: Ajout de `weights_only=False` à tous les `torch.load()`

2. **Erreur `ValueError: first stage model`**
   - **Cause**: Config manquait `second_stage_load_pretrained: true`
   - **Solution**: Config complète uploadée sur GitHub

3. **Erreur `soundfile.LibsndfileError`**
   - **Cause**: Metadata.json contenait des UUIDs au lieu des transcriptions
   - **Solution**: Génération de `metadata_correct.json` depuis le CSV Gemini (1509 → 1052 entrées valides)

4. **Erreur `TypeError: ASRCNN got dim_in`**
   - **Cause**: Config ASR corrompue avec `dim_in` au lieu de `input_dim`
   - **Solution**: Régénération complète de `Utils/ASR/config.yml`

5. **Erreur `CUDA out of memory` sur T4**
   - **Cause**: Modèle trop lourd pour 15GB VRAM (T4)
   - **Solution**: Migration vers A100 (80GB) ou réduction `batch_size=2, max_len=200`

---

## 📂 Fichiers Clés Créés/Modifiés

### Sur GitHub (`Racim679/tts`)

```
StyleTTS2/
├── Configs/
│   └── config_darija_ft.yml         ✅ Config correcte (hifigan decoder, second_stage=true)
├── Utils/
│   ├── ASR/config.yml               ✅ input_dim=80, token_embedding_dim=512
│   └── PLBERT/util.py               ✅ Patché weights_only=False
├── models.py                         ✅ Patché weights_only=False
├── train_finetune.py                 ✅ num_workers=0, debug prints
└── .gitignore                        ✅ Exclut .pth et .wav

metadata_correct.json                 ✅ 1509 transcriptions Darija (filtré à 1052)
```

### En Local (non commité)

```
C:\Users\Racim\Desktop\arable tts - Copie/
├── gemini_audio_transcription_rows (1).csv  📄 Source des transcriptions
├── fix_metadata_noemoji.py                   🔧 Script de génération metadata
└── metadata_correct.json                     ✅ 1509 entrées originales
```

---

## ⚙️ Configuration Finale

### Pour A100 (80GB VRAM)

```yaml
# Configs/config_darija_ft.yml
batch_size: 16
max_len: 400
pretrained_model: Models/LibriTTS/epochs_2nd_00020.pth
second_stage_load_pretrained: true
load_only_params: true

model_params:
  decoder:
    type: hifigan  # ⚠️ CRITIQUE (pas istftnet)

data_params:
  root_path: /content/StyleTTS2
  train_data: Data/train_list.txt
  val_data: Data/val_list.txt
```

### Pour T4 (15GB VRAM) - Alternative

```yaml
batch_size: 2
max_len: 200
slmadv_params:
  min_len: 150
  max_len: 250
```

---

## 🗂️ Dataset

### Structure du Metadata Correct

```json
{
  "audio_file": "wavs/audio_107_seg057.wav",
  "text": "لوجون لي هنا في القبه بسومه 8 ملاير و200...",
  "speaker_id": "692"
}
```

### Statistiques

- **Total fichiers audio**: 1052 `.wav`
- **Total transcriptions valides**: 1052 (filtré depuis 1509)
- **Train samples**: 999
- **Val samples**: 53
- **Sample rate**: 48kHz (à resampler à 24kHz par StyleTTS2)

---

## 🚀 Cellules Colab Finales

### 1. Setup Initial

```python
# Installation dépendances
!pip install -q phonemizer==3.2.1 munch accelerate transformers einops tqdm
!pip install -q git+https://github.com/resemble-ai/monotonic_align.git
!apt-get install -qq espeak-ng
```

### 2. Téléchargement Code + Modèles

```python
# Cloner StyleTTS2 original
!git clone https://github.com/yl4579/StyleTTS2.git /content/StyleTTS2

# Télécharger checkpoints pré-entraînés
!mkdir -p /content/StyleTTS2/Models/LibriTTS
!wget -O /content/StyleTTS2/Models/LibriTTS/epochs_2nd_00020.pth \
    https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/epochs_2nd_00020.pth

# Télécharger Utils (ASR, PLBERT, JDC)
!wget -O /content/StyleTTS2/Utils/ASR/epoch_00080.pth \
    https://github.com/yl4579/StyleTTS2/raw/main/Utils/ASR/epoch_00080.pth
# ... (voir notebook complet)
```

### 3. Correction Metadata + Config

```python
# Télécharger metadata correct depuis GitHub
import requests
url = "https://raw.githubusercontent.com/Racim679/tts/main/metadata_correct.json"
metadata = requests.get(url).json()

# Filtrer pour fichiers existants
# Générer train_list.txt et val_list.txt
# (voir code complet dans TROUBLESHOOTING)
```

### 4. Réinitialisation Config

```python
# Télécharger config correcte depuis GitHub
config_url = "https://raw.githubusercontent.com/Racim679/tts/main/StyleTTS2/Configs/config_darija_ft.yml"
config = yaml.safe_load(requests.get(config_url).text)

# Ajuster pour A100
config['batch_size'] = 16
config['data_params']['root_path'] = '/content/StyleTTS2'

# Sauvegarder
with open('/content/StyleTTS2/Configs/config_darija_ft.yml', 'w') as f:
    yaml.dump(config, f)
```

### 5. Lancement Training

```python
%cd /content/StyleTTS2
!python train_finetune.py --config_path Configs/config_darija_ft.yml
```

---

## 🐛 Erreurs Communes & Solutions

| Erreur | Cause | Solution |
|--------|-------|----------|
| `weights_only is invalid keyword` | Syntaxe PyTorch incorrecte | `str(iters, weights_only=False)` → `str(iters)` + `weights_only=False` dans `torch.load()` |
| `ValueError: first stage model` | `second_stage_load_pretrained` manquant | Ajouter `second_stage_load_pretrained: true` |
| `soundfile.LibsndfileError` | Textes sont des UUIDs | Utiliser `metadata_correct.json` |
| `TypeError: ASRCNN got dim_in` | Config ASR corrompue | Utiliser `input_dim` au lieu de `dim_in` |
| `CUDA out of memory` | Batch trop gros pour GPU | Réduire `batch_size` et `max_len` |
| `decoder type: istftnet` | Mauvaise config | Forcer `decoder.type: hifigan` |

---

## 📊 Performance Attendue

### Avec A100

- **Durée totale**: 6-8 heures (80 epochs)
- **Batch size**: 16
- **Samples/sec**: ~50-60
- **Checkpoints**: Sauvegardés tous les 10 epochs

### Avec T4 (fallback)

- **Durée totale**: 24-30 heures (80 epochs)
- **Batch size**: 2
- **Samples/sec**: ~10-15

---

## 🔄 Workflow Git

### Commits Principaux

```bash
6290915  Add StyleTTS2 with Darija config and PyTorch 2.6 patches
efd92d6  Add correct metadata.json with real Darija transcriptions (1509 samples)
```

### Structure GitHub

```
https://github.com/Racim679/tts/
├── StyleTTS2/          # Code StyleTTS2 modifié
├── metadata_correct.json  # Transcriptions valides
└── dataset_training/   # (local uniquement, exclu par .gitignore)
```

---

## 📝 Notes Importantes

1. **Checkpoints pré-entraînés**: Ne JAMAIS commit les `.pth` (735MB) sur GitHub
2. **Audio files**: Hébergés sur HuggingFace: `RacimPoly6/darija-tts-dataset`
3. **Transcriptions source**: CSV Supabase `gemini_audio_transcription_rows (1).csv`
4. **Encoder UTF-8**: Toujours utiliser `encoding='utf-8'` pour les fichiers arabes
5. **Windows CP1252**: Éviter les emojis dans les scripts Python locaux

---

## 🎯 Prochaines Étapes

1. ✅ **Lancer le training sur A100** avec la config finale
2. ⏳ **Surveiller TensorBoard** pour loss convergence
3. 💾 **Sauvegarder checkpoints** sur Google Drive tous les 10 epochs
4. 🧪 **Tester inférence** avec `epoch_2nd_00050.pth` (après ~4h)
5. 📤 **Upload modèle final** sur HuggingFace après training complet

---

## 🔗 Ressources

- **Repo GitHub**: https://github.com/Racim679/tts
- **Dataset HuggingFace**: https://huggingface.co/datasets/RacimPoly6/darija-tts-dataset
- **StyleTTS2 Original**: https://github.com/yl4579/StyleTTS2
- **Checkpoint LibriTTS**: https://huggingface.co/yl4579/StyleTTS2-LibriTTS

---

## 🆘 Support

Si problèmes lors du prochain training :

1. **Vérifier les configs** :
   ```python
   # Config principale
   second_stage_load_pretrained: true  # ⚠️ CRITIQUE
   decoder.type: hifigan                # ⚠️ CRITIQUE

   # Config ASR
   input_dim: 80                        # ⚠️ PAS dim_in !
   token_embedding_dim: 512             # ⚠️ CRITIQUE
   ```

2. **Nettoyer mémoire GPU** :
   ```python
   torch.cuda.empty_cache()
   gc.collect()
   ```

3. **Restaurer config depuis GitHub** :
   ```bash
   wget https://raw.githubusercontent.com/Racim679/tts/main/StyleTTS2/Configs/config_darija_ft.yml
   ```

---

**Généré le**: 2025-12-10
**Dernière mise à jour**: 2025-12-10 18:30 UTC
**Statut**: ✅ Prêt pour production sur A100
