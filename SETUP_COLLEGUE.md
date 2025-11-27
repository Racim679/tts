# Guide de Setup pour Collègue

## Étapes rapides pour démarrer l'entraînement

### 1. Récupérer le projet

```bash
git clone <URL_DU_REPO>
cd "arable tts"
```

### 2. Setup rapide (PowerShell)

```powershell
# Créer environnement virtuel
python -m venv venv_tts
.\venv_tts\Scripts\Activate.ps1

# Installer dépendances
pip install TTS torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install soundfile pandas python-dotenv google-generativeai

# Vérifier GPU
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}, VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB' if torch.cuda.is_available() else 'Pas de GPU')"
```

### 3. Télécharger les fichiers du modèle (si nécessaire)

Le modèle sera téléchargé automatiquement, mais si vous voulez le faire manuellement :

```python
python -c "from TTS.utils.manage import ModelManager; ModelManager().download_model('tts_models/multilingual/multi-dataset/xtts_v2')"
```

### 4. Vérifier le dataset

```bash
python -c "import json; data = json.load(open('dataset_training/metadata.json', 'r', encoding='utf-8')); print(f'Total fichiers: {len(data)}')"
```

Devrait afficher : `Total fichiers: 1518`

### 5. Lancer l'entraînement

```powershell
.\lancer_entrainement.ps1
```

## Fichiers à partager séparément (trop volumineux pour Git)

Si vous avez déjà des checkpoints entraînés, partagez le dossier `xtts_finetuned/` via :

- **Google Drive** (recommandé)
- **OneDrive**
- **USB/Disque externe**

## Vérifications avant de lancer

✅ GPU détecté avec 24GB VRAM  
✅ Dataset présent (1518 fichiers)  
✅ FFmpeg installé  
✅ Environnement virtuel activé  

## Problèmes courants

**"CUDA out of memory"**  
→ Réduire `BATCH_SIZE` à 2 dans `train_xtts_simple.py`

**"FFmpeg not found"**  
→ Installer FFmpeg : `choco install ffmpeg`

**"Module not found"**  
→ Vérifier que l'environnement virtuel est activé

## Suivi de l'entraînement

```bash
# Dans un autre terminal
tensorboard --logdir xtts_finetuned/run/training/
```

Puis ouvrir http://localhost:6006

