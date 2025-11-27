# 📚 Guide: GitHub + Hugging Face pour Darija TTS

Ce guide explique comment utiliser votre projet avec GitHub (code) et Hugging Face (audio).

## 🎯 Architecture

```
GitHub (arable-tts)           Hugging Face (darija-dataset)
├── Scripts Python            ├── wavs/
├── Notebooks                 │   ├── audio001.wav
├── Configs                   │   ├── audio002.wav
└── README.md                 │   └── ...
                              ├── metadata_train.csv
                              ├── metadata_eval.csv
                              └── metadata.json
```

---

## 📤 ÉTAPE 1: Upload du Dataset sur Hugging Face

### 1.1. Créer un dataset sur Hugging Face

1. Allez sur https://huggingface.co/new-dataset
2. Créez un nouveau dataset (exemple: `votre-username/darija-dataset`)
3. Créez un token d'accès:
   - https://huggingface.co/settings/tokens
   - Créez un token avec permission **write**

### 1.2. Installer les dépendances

```bash
pip install huggingface_hub
```

### 1.3. Upload automatique

Utilisez le script fourni:

```bash
python upload_to_huggingface.py \
  --token VOTRE_TOKEN_HF \
  --repo votre-username/darija-dataset \
  --dataset-path dataset_training
```

**Ou avec variable d'environnement:**

```bash
# Windows PowerShell
$env:HF_TOKEN="votre_token"
python upload_to_huggingface.py --repo votre-username/darija-dataset

# Linux/Mac
export HF_TOKEN="votre_token"
python upload_to_huggingface.py --repo votre-username/darija-dataset
```

### 1.4. Vérification

Allez sur `https://huggingface.co/datasets/votre-username/darija-dataset`

Vous devriez voir:
- ✅ Dossier `wavs/` avec tous vos fichiers audio
- ✅ `metadata_train.csv`
- ✅ `metadata_eval.csv`
- ✅ `metadata.json`

---

## 🐙 ÉTAPE 2: Mettre le Code sur GitHub

### 2.1. Initialiser Git (si pas déjà fait)

```bash
cd "C:\Users\Racim\Desktop\arable tts"
git init
```

### 2.2. Vérifier le .gitignore

Le fichier `.gitignore` est déjà configuré pour exclure:
- ❌ Fichiers audio (*.wav, *.mp3, *.m4a)
- ❌ Modèles (*.pth, *.pt)
- ❌ Dossier `dataset_training/wavs/`
- ❌ Token Hugging Face

### 2.3. Créer un repo sur GitHub

1. Allez sur https://github.com/new
2. Créez un nouveau repo (exemple: `arable-tts`)
3. **NE PAS** initialiser avec README (vous en avez déjà un)

### 2.4. Push vers GitHub

```bash
# Ajouter tous les fichiers
git add .

# Créer le premier commit
git commit -m "Initial commit: Darija TTS avec GitHub + HuggingFace"

# Lier au repo distant
git remote add origin https://github.com/votre-username/arable-tts.git

# Push
git branch -M main
git push -u origin main
```

---

## 🚀 ÉTAPE 3: Utiliser dans Google Colab

### 3.1. Ouvrir le notebook

1. Uploadez `COLAB_NOTEBOOK_FINAL.ipynb` sur votre Google Drive
2. Ouvrez-le avec Google Colab
3. **OU** créez un nouveau notebook et copiez les cellules

### 3.2. Configurer les repos

Dans la première cellule de configuration:

```python
GITHUB_REPO = "votre-username/arable-tts"
HF_DATASET_REPO = "votre-username/darija-dataset"
HF_TOKEN = ""  # Laissez vide si dataset public
```

### 3.3. Exécuter le notebook

1. **Runtime → Change runtime type → GPU (T4)**
2. Exécutez toutes les cellules dans l'ordre
3. Le dataset sera téléchargé automatiquement depuis Hugging Face

---

## 🔄 Workflow Complet

### Workflow quotidien

```
1. Modifier le code en local
   ↓
2. git add . && git commit -m "description"
   ↓
3. git push
   ↓
4. Dans Colab: !git pull (si déjà cloné)
   ↓
5. Training avec données depuis HuggingFace
```

### Ajouter de nouveaux fichiers audio

```bash
# 1. Ajouter les fichiers dans dataset_training/wavs/
# 2. Mettre à jour metadata.json

# 3. Re-upload sur HuggingFace
python upload_to_huggingface.py \
  --token VOTRE_TOKEN \
  --repo votre-username/darija-dataset
```

---

## 📦 Scripts Disponibles

### `upload_to_huggingface.py`

Upload le dataset audio sur Hugging Face.

```bash
python upload_to_huggingface.py --token TOKEN --repo username/dataset
```

### `download_from_huggingface.py`

Télécharge le dataset localement (pour tests).

```bash
python download_from_huggingface.py --repo username/dataset --output dataset_training
```

---

## 💡 Avantages de cette Architecture

| Aspect | GitHub | Hugging Face |
|--------|--------|--------------|
| **Code Python** | ✅ | ❌ |
| **Notebooks** | ✅ | ❌ |
| **Configs** | ✅ | ❌ |
| **Fichiers audio** | ❌ | ✅ |
| **Métadonnées CSV** | ❌ | ✅ |
| **Modèles entraînés** | ❌ | ✅ |

### Pourquoi?

- **GitHub**: Limité à 100MB par fichier → Parfait pour code
- **Hugging Face**: Optimisé pour gros datasets → Parfait pour audio

---

## 🛠️ Dépannage

### Erreur: "Repository not found"

- Vérifiez que le repo existe sur Hugging Face
- Vérifiez le nom du repo (format: `username/repo-name`)

### Erreur: "Authentication failed"

- Vérifiez votre token Hugging Face
- Assurez-vous qu'il a les droits **write**

### Dataset privé

Si votre dataset est privé, ajoutez le token:

```python
HF_TOKEN = "hf_..." # Votre token
```

### Upload lent

L'upload peut prendre du temps selon:
- Nombre de fichiers audio
- Taille totale du dataset
- Vitesse de votre connexion

**Conseil:** Lancez l'upload et laissez tourner.

---

## 📝 Checklist de Setup Complet

- [ ] Dataset uploadé sur Hugging Face
- [ ] Code pushé sur GitHub
- [ ] `.gitignore` configuré (fichiers audio exclus)
- [ ] Notebook Colab testé et fonctionnel
- [ ] Token HF créé (si dataset privé)
- [ ] README mis à jour avec vos repos

---

## 🔗 Liens Utiles

- **Hugging Face Hub**: https://huggingface.co/docs/hub
- **Git Documentation**: https://git-scm.com/doc
- **Google Colab**: https://colab.research.google.com/

---

## 🎓 Partager avec un Collègue

Votre collègue doit juste:

1. Ouvrir le notebook Colab: `COLAB_NOTEBOOK_FINAL.ipynb`
2. Modifier la config avec vos repos GitHub/HuggingFace
3. Exécuter toutes les cellules
4. **C'est tout!** Pas de compression/décompression

---

## ✨ Prochaines Étapes

Une fois le training terminé:

1. Sauvegarder les checkpoints sur Drive (cellule 10)
2. Optionnel: Upload le modèle entraîné sur HuggingFace (cellule 11)
3. Utiliser `generate_finetuned_direct.py` pour la génération

---

**Bon training! 🚀**
