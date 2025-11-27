# Script pour installer Chocolatey et ffmpeg
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Installation de Chocolatey et ffmpeg" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si on est administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ATTENTION: Ce script necessite des privileges administrateur!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pour installer Chocolatey et ffmpeg:" -ForegroundColor Yellow
    Write-Host "  1. Clic droit sur PowerShell" -ForegroundColor White
    Write-Host "  2. Selectionnez 'Executer en tant qu'administrateur'" -ForegroundColor White
    Write-Host "  3. Relancez ce script" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou executez manuellement:" -ForegroundColor Yellow
    Write-Host "  Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" -ForegroundColor Cyan
    Write-Host "  choco install ffmpeg -y" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "Privileges administrateur detectes ✓" -ForegroundColor Green
Write-Host ""

# Vérifier si Chocolatey est déjà installé
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if ($chocoInstalled) {
    Write-Host "Chocolatey est deja installe ✓" -ForegroundColor Green
    Write-Host "  Version: $($chocoInstalled.Version)" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "Installation de Chocolatey..." -ForegroundColor Yellow
    Write-Host "  Cela peut prendre quelques minutes..." -ForegroundColor Gray
    Write-Host ""
    
    try {
        # Installer Chocolatey
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Rafraîchir le PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Host ""
        Write-Host "✓ Chocolatey installe avec succes!" -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Host ""
        Write-Host "✗ ERREUR lors de l'installation de Chocolatey!" -ForegroundColor Red
        Write-Host "  Erreur: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Essayez d'installer manuellement:" -ForegroundColor Yellow
        Write-Host "  Visitez: https://chocolatey.org/install" -ForegroundColor Cyan
        exit 1
    }
}

# Vérifier si ffmpeg est déjà installé
$ffmpegInstalled = Get-Command ffmpeg -ErrorAction SilentlyContinue

if ($ffmpegInstalled) {
    Write-Host "ffmpeg est deja installe ✓" -ForegroundColor Green
    Write-Host "  Version: $($ffmpegInstalled.Version)" -ForegroundColor Gray
    Write-Host ""
    
    # Vérifier la version
    $ffmpegVersion = & ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "  $ffmpegVersion" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "ffmpeg est pret a etre utilise!" -ForegroundColor Green
    exit 0
}

Write-Host "Installation de ffmpeg via Chocolatey..." -ForegroundColor Yellow
Write-Host "  Cela peut prendre quelques minutes..." -ForegroundColor Gray
Write-Host ""

try {
    # Installer ffmpeg
    choco install ffmpeg -y
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ ffmpeg installe avec succes!" -ForegroundColor Green
        Write-Host ""
        
        # Rafraîchir le PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Vérifier l'installation
        Start-Sleep -Seconds 2
        $ffmpegCheck = & ffmpeg -version 2>&1 | Select-Object -First 1
        if ($ffmpegCheck) {
            Write-Host "Verification:" -ForegroundColor Cyan
            Write-Host "  $ffmpegCheck" -ForegroundColor Gray
            Write-Host ""
            Write-Host "✓ ffmpeg est pret a etre utilise!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  ffmpeg installe mais non detecte dans le PATH" -ForegroundColor Yellow
            Write-Host "  Redemarrez PowerShell ou votre terminal" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "✗ ERREUR lors de l'installation de ffmpeg!" -ForegroundColor Red
        Write-Host "  Code de sortie: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "✗ ERREUR lors de l'installation de ffmpeg!" -ForegroundColor Red
    Write-Host "  Erreur: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Essayez d'installer manuellement:" -ForegroundColor Yellow
    Write-Host "  choco install ffmpeg -y" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Installation terminee!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vous pouvez maintenant utiliser add_m4a_to_dataset.py" -ForegroundColor Cyan
Write-Host ""


