# Script pour préparer le projet pour GitHub
# Vérifie que les fichiers sensibles/volumineux sont exclus

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Preparation du projet pour GitHub" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que .gitignore existe
if (-not (Test-Path ".gitignore")) {
    Write-Host "ERREUR: .gitignore non trouve!" -ForegroundColor Red
    exit 1
}

Write-Host "Verification des fichiers a exclure..." -ForegroundColor Yellow
Write-Host ""

# Vérifier les dossiers volumineux
$excluded = @(
    "venv_tts",
    "xtts_finetuned",
    "__pycache__",
    ".env"
)

$warnings = @()

foreach ($item in $excluded) {
    if (Test-Path $item) {
        if (Test-Path $item -PathType Container) {
            $size = (Get-ChildItem $item -Recurse -ErrorAction SilentlyContinue | 
                     Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum / 1GB
            Write-Host "  [OK] $item existe ($([math]::Round($size, 2)) GB) - sera exclu" -ForegroundColor Green
        } else {
            Write-Host "  [OK] $item existe - sera exclu" -ForegroundColor Green
        }
    } else {
        Write-Host "  - $item n'existe pas" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Verification des fichiers importants..." -ForegroundColor Yellow
Write-Host ""

$required = @(
    "train_xtts_simple.py",
    "generate_finetuned_direct.py",
    "dataset_training/metadata.json",
    "dataset_training/wavs"
)

foreach ($item in $required) {
    if (Test-Path $item) {
        Write-Host "  [OK] $item" -ForegroundColor Green
    } else {
        Write-Host "  [ERREUR] $item MANQUANT!" -ForegroundColor Red
        $warnings += $item
    }
}

Write-Host ""
Write-Host "Taille du dataset..." -ForegroundColor Yellow

if (Test-Path "dataset_training/wavs") {
    $wavCount = (Get-ChildItem "dataset_training/wavs" -Filter "*.wav").Count
    $wavSize = (Get-ChildItem "dataset_training/wavs" -Filter "*.wav" | 
                Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "  Fichiers WAV: $wavCount" -ForegroundColor Cyan
    Write-Host "  Taille totale: $([math]::Round($wavSize, 2)) GB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [ATTENTION] Le dataset est volumineux!" -ForegroundColor Yellow
    Write-Host "     GitHub a une limite de 100 MB par fichier" -ForegroundColor Yellow
    Write-Host "     Si le dataset est trop gros, utilisez Git LFS:" -ForegroundColor Yellow
    Write-Host "     git lfs install" -ForegroundColor Gray
    Write-Host "     git lfs track '*.wav'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Commandes pour initialiser Git:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "git init" -ForegroundColor White
Write-Host "git add ." -ForegroundColor White
Write-Host "git commit -m 'Initial commit - XTTS fine-tuning project'" -ForegroundColor White
Write-Host ""
Write-Host "Sur GitHub:" -ForegroundColor Yellow
Write-Host "1. Creer un nouveau repository (prive ou public)" -ForegroundColor White
Write-Host "2. git remote add origin <URL_DU_REPO>" -ForegroundColor White
Write-Host "3. git push -u origin main" -ForegroundColor White
Write-Host ""

if ($warnings.Count -gt 0) {
    Write-Host "[AVERTISSEMENTS]:" -ForegroundColor Red
    foreach ($w in $warnings) {
        Write-Host "   - $w manquant" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

