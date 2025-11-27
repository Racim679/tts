# Script PowerShell pour ajouter des fichiers M4A au dataset
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Ajout de fichiers M4A au dataset d'entrainement" -ForegroundColor Cyan
Write-Host "Conversion en WAV 48kHz (qualite maximale)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
& ".\venv_tts\Scripts\Activate.ps1"

Write-Host ""

# Vérifier les fichiers M4A
Write-Host "Recherche des fichiers M4A..." -ForegroundColor Yellow

# Chercher d'abord dans le dossier audio/
$audioDir = Join-Path $PWD "audio"
$m4aFiles = @()

if (Test-Path $audioDir -PathType Container) {
    Write-Host "Recherche dans le dossier 'audio/'..." -ForegroundColor Cyan
    $m4aFiles = Get-ChildItem -Path $audioDir -Filter "*.m4a"
}

# Si pas trouvé dans audio/, chercher dans le répertoire courant
if ($m4aFiles.Count -eq 0) {
    Write-Host "Recherche dans le repertoire courant..." -ForegroundColor Cyan
    $m4aFiles = Get-ChildItem -Filter "*.m4a"
}

if ($m4aFiles.Count -eq 0) {
    Write-Host "ERREUR: Aucun fichier M4A trouve!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Placez vos fichiers M4A dans:" -ForegroundColor Yellow
    Write-Host "  - Le dossier 'audio/' (recommandé)" -ForegroundColor White
    Write-Host "  - Ou le repertoire courant: $PWD" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "Fichiers M4A trouves: $($m4aFiles.Count)" -ForegroundColor Green
Write-Host ""

# Afficher les fichiers
Write-Host "Fichiers detectes:" -ForegroundColor Cyan
foreach ($file in $m4aFiles) {
    $sizeMB = [math]::Round($file.Length / 1MB, 2)
    Write-Host "  - $($file.Name) ($sizeMB MB)" -ForegroundColor White
}
Write-Host ""

# Vérifier si ffmpeg est disponible (nécessaire pour pydub avec M4A)
Write-Host "Verification de ffmpeg..." -ForegroundColor Yellow
try {
    $ffmpegCheck = & ffmpeg -version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ ffmpeg detecte" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  ffmpeg non detecte dans le PATH" -ForegroundColor Yellow
        Write-Host "     pydub peut quand meme fonctionner si ffmpeg est installe" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  ffmpeg non detecte dans le PATH" -ForegroundColor Yellow
    Write-Host "     pydub peut quand meme fonctionner si ffmpeg est installe" -ForegroundColor Yellow
}
Write-Host ""

# Lancer le script Python
Write-Host "Lancement de la conversion..." -ForegroundColor Yellow
Write-Host ""
python add_m4a_to_dataset.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERREUR lors de la conversion!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Conversion terminee!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

