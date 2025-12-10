# Contexte du Projet - Fine-tuning StyleTTS2 pour Darija

## 🎯 Objectif
Fine-tuner StyleTTS2 sur un dataset de **darija marocain** pour générer de la parole synthétique en dialecte.

## 📊 État Actuel (2025-12-10)

### ✅ Complété
- [x] Dataset collecté : 1052 fichiers audio avec transcriptions
- [x] Metadata nettoyé : `metadata_correct.json` (1509 → 1052 entrées valides)
- [x] Configs corrigées pour PyTorch 2.6+
- [x] Code patché et uploadé sur GitHub
- [x] Prêt pour training sur A100

### ⏳ En Cours
- [ ] Training sur A100 (80 epochs, ~6-8h)
- [ ] Validation checkpoints intermédiaires
- [ ] Upload modèle final sur HuggingFace

## 📁 Structure du Projet

```
arable-tts/
├── StyleTTS2/                    # Fork modifié de StyleTTS2
│   ├── Configs/
│   │   └── config_darija_ft.yml  # Config finale validée
│   ├── Utils/
│   │   ├── ASR/config.yml        # token_embedding_dim=512
│   │   └── PLBERT/util.py        # Patché pour PyTorch 2.6+
│   └── models.py                 # Patché weights_only=False
│
├── metadata_correct.json         # 1052 transcriptions valides
├── TROUBLESHOOTING_SESSION_2025-12-10.md  # LOG COMPLET de la session
└── CONTEXT_PROJET.md             # Ce fichier
```

## 🔗 Liens Importants

- **GitHub**: https://github.com/Racim679/tts
- **Dataset Audio**: https://huggingface.co/datasets/RacimPoly6/darija-tts-dataset
- **Checkpoint LibriTTS**: https://huggingface.co/yl4579/StyleTTS2-LibriTTS
- **Transcriptions Source**: `gemini_audio_transcription_rows (1).csv` (local)

## 🚀 Quick Start - Colab

### 1. Télécharger la config correcte depuis GitHub

```python
import requests
import yaml

# Config principale
config_url = "https://raw.githubusercontent.com/Racim679/tts/main/StyleTTS2/Configs/config_darija_ft.yml"
config = yaml.safe_load(requests.get(config_url).text)
config['data_params']['root_path'] = '/content/StyleTTS2'

with open('/content/StyleTTS2/Configs/config_darija_ft.yml', 'w') as f:
    yaml.dump(config, f)

# Config ASR
asr_config = {
    "model_params": {
        "input_dim": 80,
        "hidden_dim": 256,
        "n_token": 178,
        "n_layers": 6,
        "token_embedding_dim": 512
    }
}

with open('/content/StyleTTS2/Utils/ASR/config.yml', 'w') as f:
    yaml.dump(asr_config, f)
```

### 2. Télécharger le metadata correct

```python
# Metadata avec vraies transcriptions
metadata_url = "https://raw.githubusercontent.com/Racim679/tts/main/metadata_correct.json"
metadata = requests.get(metadata_url).json()

# Filtrer pour fichiers existants + générer train/val lists
# (voir TROUBLESHOOTING_SESSION pour le code complet)
```

### 3. Lancer le training

```python
%cd /content/StyleTTS2
!python train_finetune.py --config_path Configs/config_darija_ft.yml
```

## ⚙️ Configurations Clés

### Config Principale (`config_darija_ft.yml`)

```yaml
batch_size: 16                    # A100
max_len: 400
pretrained_model: Models/LibriTTS/epochs_2nd_00020.pth
second_stage_load_pretrained: true  # ⚠️ CRITIQUE
load_only_params: true

model_params:
  decoder:
    type: hifigan                 # ⚠️ PAS istftnet !
```

### Config ASR (`Utils/ASR/config.yml`)

```yaml
model_params:
  input_dim: 80                   # ⚠️ PAS dim_in !
  hidden_dim: 256
  n_token: 178
  n_layers: 6
  token_embedding_dim: 512        # ⚠️ CRITIQUE (doit matcher checkpoint)
```

## 🐛 Problèmes Connus & Solutions

| Problème | Solution Rapide |
|----------|-----------------|
| `ValueError: first stage model` | `second_stage_load_pretrained: true` |
| `TypeError: dim_in` | Utiliser `input_dim` dans ASR config |
| `decoder type: istftnet` | Forcer `type: hifigan` |
| Textes = UUIDs | Utiliser `metadata_correct.json` |
| CUDA OOM | Réduire `batch_size` ou migrer A100 |

**Voir `TROUBLESHOOTING_SESSION_2025-12-10.md` pour détails complets.**

## 📝 Dataset

### Statistiques
- **Audio files**: 1052 `.wav` (48kHz)
- **Transcriptions**: 1052 (arabe + darija mélangé)
- **Train**: 999 samples
- **Val**: 53 samples
- **Durée totale**: ~45 minutes

### Format Metadata

```json
{
  "audio_file": "wavs/audio_107_seg057.wav",
  "text": "لوجون لي هنا في القبه بسومه 8 ملاير و200...",
  "speaker_id": "692"
}
```

## 🔄 Workflow de Développement

### Sur Colab
1. Cloner StyleTTS2 original
2. Télécharger checkpoints pré-entraînés
3. Appliquer configs depuis GitHub
4. Générer train/val lists depuis metadata_correct.json
5. Lancer training

### Sur Local
1. Tester modifications dans `StyleTTS2/`
2. Commit sur `Racim679/tts`
3. Utiliser depuis Colab via GitHub

## 📦 Dépendances Principales

```
phonemizer==3.2.1
torch>=2.0
transformers
einops
munch
monotonic_align (depuis GitHub)
```

## 🎯 Prochaines Sessions

### À Faire
1. **Monitoring training**: TensorBoard, loss curves
2. **Test inférence**: Après epoch 50
3. **Optimisation**: Si qualité insuffisante
4. **Upload final**: HuggingFace après training complet

### À Vérifier
- [ ] Convergence du loss après 20 epochs
- [ ] Qualité audio des samples générés
- [ ] Prononciation correcte du darija
- [ ] Absence d'artefacts

## 📞 Contact / Notes

**Développeur**: Racim
**Date Démarrage**: 2025-12-10
**Status**: Prêt pour training A100

---

**⚠️ IMPORTANT**: Toujours utiliser les configs depuis GitHub, jamais les configs locales de Colab qui peuvent être corrompues !

**📖 Doc Complète**: `TROUBLESHOOTING_SESSION_2025-12-10.md`
