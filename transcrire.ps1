# Script PowerShell pour lancer la transcription avec Gemini
# Transcription intelligente en Darija algérienne

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Transcription audio avec Gemini Flash 2.0 exp" -ForegroundColor Cyan
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
Write-Host "Lancement de la transcription..." -ForegroundColor Green
Write-Host ""

# Lancer le script Python
python transcribe_with_gemini.py

# Attendre que l'utilisateur appuie sur une touche avant de fermer
Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

