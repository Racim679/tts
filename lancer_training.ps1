# Script pour lancer le training XTTS-v2
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "XTTS-v2 - Preparation et Training" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
& ".\venv_tts\Scripts\Activate.ps1"

Write-Host ""

# Vérifier les fichiers WAV
Write-Host "Recherche des fichiers WAV..." -ForegroundColor Yellow

# Chercher d'abord dans le dossier audio/
$audioDir = Join-Path $PWD "audio"
if (Test-Path $audioDir -PathType Container) {
    Write-Host "Recherche dans le dossier 'audio/'..." -ForegroundColor Cyan
    $wavFiles = Get-ChildItem -Path $audioDir -Filter "*.wav" | Where-Object { $_.Name -notmatch "reference|output" }
} else {
    $wavFiles = @()
}

# Si pas trouvé dans audio/, chercher dans le répertoire courant
if ($wavFiles.Count -eq 0) {
    Write-Host "Recherche dans le repertoire courant..." -ForegroundColor Cyan
    $wavFiles = Get-ChildItem -Filter "*.wav" | Where-Object { $_.Name -notmatch "reference|output" }
}

if ($wavFiles.Count -eq 0) {
    Write-Host "ERREUR: Aucun fichier WAV trouve!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Placez vos 10 fichiers WAV dans:" -ForegroundColor Yellow
    Write-Host "  - Le dossier 'audio/' (recommandé)" -ForegroundColor White
    Write-Host "  - Ou le repertoire courant: $PWD" -ForegroundColor White
    Write-Host ""
    Write-Host "Les fichiers peuvent avoir n'importe quel nom (ex: ReelAudio-XXXXX.wav)" -ForegroundColor Yellow
    exit 1
}

Write-Host "Fichiers WAV trouves: $($wavFiles.Count)" -ForegroundColor Green
Write-Host ""

# Afficher les fichiers
Write-Host "Fichiers detectes:" -ForegroundColor Cyan
foreach ($file in $wavFiles) {
    $sizeMB = [math]::Round($file.Length / 1MB, 2)
    Write-Host "  - $($file.Name) ($sizeMB MB)" -ForegroundColor White
}
Write-Host ""

# Vérifier si les données sont déjà préparées
$datasetDir = "dataset_training"
$metadataFile = Join-Path $datasetDir "metadata.json"

if (Test-Path $metadataFile) {
    Write-Host "ATTENTION: Des donnees sont deja preparees!" -ForegroundColor Yellow
    Write-Host "  Fichier: $metadataFile" -ForegroundColor White
    Write-Host ""
    $response = Read-Host "Voulez-vous re-preparer les donnees? (oui/non)"
    if ($response -match "^(oui|o|yes|y)$") {
    Write-Host ""
    Write-Host "Preparation des donnees..." -ForegroundColor Yellow
    python prepare_training_data_with_file.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERREUR lors de la preparation!" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "Preparation des donnees..." -ForegroundColor Yellow
    Write-Host ""
    python prepare_training_data_with_file.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR lors de la preparation!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Pret pour le training!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Demander confirmation pour lancer le training
Write-Host "Le training va commencer. Cela peut prendre 2-4 heures." -ForegroundColor Yellow
Write-Host ""
$response = Read-Host "Lancer le training maintenant? (oui/non)"

if ($response -match "^(oui|o|yes|y)$") {
    Write-Host ""
    Write-Host "Lancement du training..." -ForegroundColor Green
    Write-Host ""
    python train_xtts.py
} else {
    Write-Host ""
    Write-Host "Training annule." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour lancer le training plus tard:" -ForegroundColor Cyan
    Write-Host "  python train_xtts.py" -ForegroundColor White
}

