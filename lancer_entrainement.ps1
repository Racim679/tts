# Script PowerShell pour lancer l'entraînement XTTS-v2
# Configuration optimisée pour 48 kHz - Qualité maximale

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Lancement de l'entrainement XTTS-v2" -ForegroundColor Cyan
Write-Host "Configuration: 48 kHz, FP32, Qualite maximale" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
if (Test-Path "venv_tts\Scripts\Activate.ps1") {
    Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
    & .\venv_tts\Scripts\Activate.ps1
} else {
    Write-Host "ERREUR: Environnement virtuel non trouve!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Lancement de l'entrainement..." -ForegroundColor Green
Write-Host "ATTENTION: Cela peut prendre plusieurs heures!" -ForegroundColor Yellow
Write-Host ""

# Lancer le script Python
python train_xtts_simple.py

# Attendre que l'utilisateur appuie sur une touche avant de fermer
Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

