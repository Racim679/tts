# Script PowerShell pour générer de l'audio avec le modèle fine-tuné
# Utilise le Python de l'environnement virtuel

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Cyan
& ".\venv_tts\Scripts\python.exe" "generate_finetuned_direct.py"

