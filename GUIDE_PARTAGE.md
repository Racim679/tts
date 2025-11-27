# Guide de Partage du Projet - Stratégie Optimale

## 🎯 Meilleure Approche : GitHub + Partage Séparé des Fichiers Volumineux

### Option 1 : GitHub (Recommandé) ⭐

**Avantages :**
- Version control automatique
- Collaboration facile
- Historique des changements
- Accès depuis n'importe où

**Étapes :**

1. **Créer un repository GitHub** (privé ou public selon vos besoins)
   - Aller sur https://github.com/new
   - Nom suggéré : `xtts-darija-finetuning`
   - Cocher "Private" si vous voulez garder le projet privé

2. **Initialiser Git localement :**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit - XTTS fine-tuning project"
   ```

3. **Connecter au repository GitHub :**
   ```powershell
   git remote add origin https://github.com/VOTRE_USERNAME/xtts-darija-finetuning.git
   git branch -M main
   git push -u origin main
   ```

4. **Partager l'URL HTTPS avec votre collègue :**
   ```
   https://github.com/VOTRE_USERNAME/xtts-darija-finetuning.git
   ```

5. **Pour les fichiers volumineux (checkpoints, dataset) :**
   - **Option A : Git LFS** (pour fichiers < 2GB)
     ```powershell
     git lfs install
     git lfs track "*.wav"
     git lfs track "*.pth"
     git add .gitattributes
     git commit -m "Add Git LFS tracking"
     ```
   
   - **Option B : Partage séparé** (recommandé pour gros fichiers)
     - Uploader `xtts_finetuned/` sur Google Drive / OneDrive
     - Partager le lien avec votre collègue
     - Il télécharge et place dans le projet

### Option 2 : Archive ZIP + Cloud Storage

**Quand utiliser :**
- Si vous ne voulez pas utiliser Git
- Pour un partage ponctuel

**Étapes :**

1. **Créer une archive sans fichiers volumineux :**
   ```powershell
   # Exclure venv, checkpoints, etc.
   Compress-Archive -Path * -DestinationPath projet_xtts.zip -Exclude venv_tts,xtts_finetuned,__pycache__
   ```

2. **Uploader sur :**
   - Google Drive
   - OneDrive
   - Dropbox
   - WeTransfer (pour fichiers < 2GB)

3. **Partager les fichiers volumineux séparément :**
   - Dataset WAV : Archive séparée ou lien cloud
   - Checkpoints : Si déjà entraînés, partager `xtts_finetuned/`

### Option 3 : USB / Disque Externe

**Quand utiliser :**
- Transfert local rapide
- Pas d'accès internet fiable
- Fichiers très volumineux

**Étapes :**
1. Copier tout le dossier du projet
2. Exclure `venv_tts/` (il devra le recréer)
3. Inclure `dataset_training/` et scripts
4. Optionnel : Inclure `xtts_finetuned/` si checkpoints existent

## 📋 Checklist Avant Partage

### ✅ À Inclure dans Git/Archive :
- [x] Tous les scripts Python (`.py`)
- [x] `dataset_training/metadata.json`
- [x] `dataset_training/wavs/` (ou utiliser Git LFS)
- [x] `README.md`, `SETUP_COLLEGUE.md`
- [x] `.gitignore`
- [x] Scripts PowerShell (`.ps1`)

### ❌ À Exclure (déjà dans `.gitignore`) :
- [x] `venv_tts/` (environnement virtuel - à recréer)
- [x] `xtts_finetuned/` (checkpoints - partager séparément si nécessaire)
- [x] `.env` (clés API - ne JAMAIS partager)
- [x] `__pycache__/`
- [x] Fichiers audio de sortie temporaires

## 🔐 Sécurité

**IMPORTANT : Ne JAMAIS partager :**
- Fichier `.env` (contient votre clé API Gemini)
- Clés API, tokens, mots de passe
- Données personnelles sensibles

**Solution :**
- Créer un fichier `.env.example` avec des valeurs factices
- Documenter dans le README comment obtenir les clés

## 🚀 Setup Rapide pour Votre Collègue

Une fois qu'il a le projet :

1. **Cloner (si GitHub) :**
   ```bash
   git clone https://github.com/VOTRE_USERNAME/xtts-darija-finetuning.git
   cd xtts-darija-finetuning
   ```

2. **Suivre `SETUP_COLLEGUE.md`** (déjà inclus dans le projet)

3. **Télécharger les fichiers volumineux** (si partagés séparément)

## 💡 Recommandation Finale

**Stratégie optimale :**

1. **GitHub pour le code** (scripts, config, metadata)
   - Facilite la collaboration
   - Version control
   - Facile à cloner

2. **Google Drive / OneDrive pour les données volumineuses**
   - Dataset WAV (si > 1GB)
   - Checkpoints entraînés (si existants)
   - Partage de lien direct

3. **Documentation claire**
   - `README.md` : Vue d'ensemble
   - `SETUP_COLLEGUE.md` : Guide de setup rapide
   - Instructions dans les scripts

**Avantages :**
- ✅ Code versionné et accessible
- ✅ Fichiers volumineux partagés efficacement
- ✅ Setup rapide pour le collègue
- ✅ Pas de limite de taille

## 📞 Support

Si votre collègue rencontre des problèmes :
1. Vérifier `SETUP_COLLEGUE.md`
2. Vérifier les logs d'erreur
3. S'assurer que tous les fichiers volumineux sont téléchargés

