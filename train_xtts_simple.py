#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplifié pour le fine-tuning de XTTS-v2
Utilise la méthode recommandée par Coqui TTS
"""

import sys
import os
from pathlib import Path

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    import multiprocessing
    multiprocessing.freeze_support()  # Nécessaire pour Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import torch
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig
from TTS.utils.manage import ModelManager

def main():
    """Fonction principale pour éviter les problèmes de multiprocessing sur Windows"""
    
    print("=" * 60)
    print("Fine-tuning XTTS-v2 - Version Simplifiee")
    print("=" * 60)
    print()

    # Vérifier GPU
    has_gpu = torch.cuda.is_available()
    if has_gpu:
        print(f"Device: cuda")
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        device = "cuda"
    else:
        print("Device: cpu")
        print("  ATTENTION: L'entrainement sur CPU sera tres lent!")
        device = "cpu"

    print()

    # Vérifier les données
    # Utiliser les segments découpés si disponibles
    dataset_dir = Path("dataset_training")
    if (dataset_dir / "metadata.json").exists():
        metadata_file = dataset_dir / "metadata.json"
    else:
        # Fallback vers segments
        dataset_dir = Path("dataset_training_segments")
        metadata_file = dataset_dir / "metadata.json"

    if not metadata_file.exists():
        print(f"ERREUR: Fichier de metadonnees non trouve: {metadata_file}")
        print("  Lancez d'abord: python prepare_training_data_with_file.py")
        exit(1)

    print(f"Dataset: {dataset_dir.absolute()}")
    print(f"Metadata: {metadata_file}")
    print()

    # Convertir metadata.json en format CSV pour XTTS
    print("Conversion du format de donnees...")
    import json
    import pandas as pd

    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Convertir en DataFrame
    df = pd.DataFrame(metadata)

    # Séparer train/eval (80/20)
    df = df.sample(frac=1).reset_index(drop=True)
    num_val = max(1, int(len(df) * 0.2))
    df_eval = df[:num_val]
    df_train = df[num_val:]

    # Créer les fichiers CSV
    train_csv = dataset_dir / "metadata_train.csv"
    eval_csv = dataset_dir / "metadata_eval.csv"

    df_train.to_csv(train_csv, sep="|", index=False)
    df_eval.to_csv(eval_csv, sep="|", index=False)

    print(f"  Train: {len(df_train)} fichiers")
    print(f"  Eval: {len(df_eval)} fichiers")
    print()

    # Configuration
    print("Configuration de l'entrainement...")
    print()

    OUT_PATH = Path("xtts_finetuned")
    OUT_PATH.mkdir(exist_ok=True)
    RUN_PATH = OUT_PATH / "run" / "training"
    RUN_PATH.mkdir(parents=True, exist_ok=True)

    # Télécharger les fichiers XTTS si nécessaire
    CHECKPOINTS_OUT_PATH = RUN_PATH / "XTTS_v2.0_original_model_files"
    CHECKPOINTS_OUT_PATH.mkdir(exist_ok=True)

    DVAE_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/dvae.pth"
    MEL_NORM_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/mel_stats.pth"
    TOKENIZER_FILE_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/vocab.json"
    XTTS_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/model.pth"
    XTTS_CONFIG_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/config.json"

    DVAE_CHECKPOINT = CHECKPOINTS_OUT_PATH / "dvae.pth"
    MEL_NORM_FILE = CHECKPOINTS_OUT_PATH / "mel_stats.pth"
    TOKENIZER_FILE = CHECKPOINTS_OUT_PATH / "vocab.json"
    XTTS_CHECKPOINT = CHECKPOINTS_OUT_PATH / "model.pth"
    XTTS_CONFIG_FILE = CHECKPOINTS_OUT_PATH / "config.json"

    # Télécharger les fichiers nécessaires
    files_to_download = []
    if not DVAE_CHECKPOINT.exists():
        files_to_download.append(DVAE_CHECKPOINT_LINK)
    if not MEL_NORM_FILE.exists():
        files_to_download.append(MEL_NORM_LINK)
    if not TOKENIZER_FILE.exists():
        files_to_download.append(TOKENIZER_FILE_LINK)
    if not XTTS_CHECKPOINT.exists():
        files_to_download.append(XTTS_CHECKPOINT_LINK)
    if not XTTS_CONFIG_FILE.exists():
        files_to_download.append(XTTS_CONFIG_LINK)

    if files_to_download:
        print("Telechargement des fichiers XTTS-v2...")
        print("(Cela peut prendre quelques minutes)")
        print()
        ModelManager._download_model_files(files_to_download, str(CHECKPOINTS_OUT_PATH), progress_bar=True)
        print()

    # Configuration du dataset
    config_dataset = BaseDatasetConfig(
        formatter="coqui",
        dataset_name="darija_dataset",
        path=str(dataset_dir.absolute()),
        meta_file_train=str(train_csv.name),
        meta_file_val=str(eval_csv.name),
        language="ar",  # Arabe pour Darija
    )

    # Paramètres du modèle - OPTIMISÉS POUR 48kHz QUALITÉ MAXIMALE
    model_args = GPTArgs(
        max_conditioning_length=288000,  # 6 secs à 48kHz (48000*6)
        min_conditioning_length=144000,  # 3 secs à 48kHz (48000*3)
        debug_loading_failures=False,
        max_wav_length=480000,  # ~10 seconds à 48kHz (48000*10)
        max_text_length=200,
        mel_norm_file=str(MEL_NORM_FILE),
        dvae_checkpoint=str(DVAE_CHECKPOINT),
        xtts_checkpoint=str(XTTS_CHECKPOINT),
        tokenizer_file=str(TOKENIZER_FILE),
        gpt_num_audio_tokens=1026,
        gpt_start_audio_token=1024,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )

    audio_config = XttsAudioConfig(sample_rate=48000, dvae_sample_rate=48000, output_sample_rate=48000)

    # Configuration d'entraînement - QUALITÉ MAXIMALE pour 24GB VRAM
    BATCH_SIZE = 4 if has_gpu else 1  # Optimisé pour 24GB VRAM
    GRAD_ACUMM_STEPS = 4  # Réduit car batch size augmenté
    NUM_EPOCHS = 120  # Plus d'époques = meilleure convergence et qualité

    # Charger la config XTTS de base
    from TTS.tts.configs.xtts_config import XttsConfig
    base_config = XttsConfig()
    base_config.load_json(str(XTTS_CONFIG_FILE))

    # Créer la config de training
    config = GPTTrainerConfig()
    config.load_json(str(XTTS_CONFIG_FILE))  # Charger depuis le fichier de base

    # Mettre à jour avec les paramètres de training
    config.lr = 3e-6  # Learning rate plus conservateur pour stabilité et qualité
    config.epochs = NUM_EPOCHS
    config.output_path = str(RUN_PATH)
    config.batch_size = BATCH_SIZE
    config.batch_group_size = 64  # Augmenté pour meilleure utilisation VRAM
    config.eval_batch_size = BATCH_SIZE
    # Sur Windows, mettre workers à 0 pour éviter les problèmes de multiprocessing
    if sys.platform == 'win32':
        config.num_loader_workers = 0
        config.num_eval_loader_workers = 0
    else:
        config.num_loader_workers = 8
        config.num_eval_loader_workers = 4
    config.run_name = "XTTS_Darija_FT"
    config.project_name = "XTTS_trainer"
    config.dashboard_logger = "tensorboard"
    config.logger_uri = None
    config.test_delay_epochs = -1
    config.save_best_after = 10
    config.save_checkpoint = True
    config.save_n_checkpoints = 5  # Plus de checkpoints pour choisir le meilleur
    config.save_all_best = False
    config.target_loss = "loss"
    config.print_step = 25
    config.plot_step = 100
    config.log_model_every_n_steps = 1000
    config.run_eval = True
    config.test_delay_epochs = 5
    config.grad_accum_steps = GRAD_ACUMM_STEPS
    config.grad_clip = 1.0  # Gradient clipping pour éviter les explosions de gradient
    config.datasets = [config_dataset]

    # Configuration de l'optimizer (IMPORTANT pour éviter l'erreur)
    config.optimizer = "AdamW"
    config.optimizer_wd_only_on_weights = True  # Pour multi-GPU, mettre False
    config.optimizer_params = {"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-2}

    # Configuration du scheduler
    config.lr_scheduler = "MultiStepLR"
    config.lr_scheduler_params = {"milestones": [50000 * 18, 150000 * 18, 300000 * 18], "gamma": 0.5, "last_epoch": -1}

    # Ajouter les arguments du modèle
    config.model_args = model_args
    config.audio = audio_config
    
    # Configuration pour qualité maximale - FP32 au lieu de FP16
    config.mixed_precision = False  # Désactiver mixed precision
    config.precision = "fp32"  # FP32 pour précision maximale (plus lent mais meilleure qualité)
    config.use_grad_scaler = False  # Pas besoin avec FP32

    print("Configuration - QUALITÉ MAXIMALE:")
    print(f"  Sample rate: 48kHz (qualité maximale)")
    print(f"  Précision: FP32 (qualité maximale)")
    print(f"  Epoques: {NUM_EPOCHS}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Gradient accumulation: {GRAD_ACUMM_STEPS}")
    print(f"  Learning rate: {config.lr}")
    print(f"  Gradient clipping: {config.grad_clip}")
    print(f"  Output: {RUN_PATH}")
    print()
    if has_gpu:
        print("⚠️  ATTENTION: Cette configuration utilise beaucoup de VRAM!")
        print(f"   VRAM estimée: ~20-22 GB")
        print()

    # Charger les données
    print("Chargement des donnees...")
    train_samples, eval_samples = load_tts_samples([config_dataset], eval_split=True, eval_split_max_size=500, eval_split_size=0.2)
    print(f"  Train samples: {len(train_samples)}")
    print(f"  Eval samples: {len(eval_samples)}")
    print()

    # Avertissement
    print("=" * 60)
    print("CONFIGURATION QUALITÉ MAXIMALE")
    print("=" * 60)
    print()
    print("Configuration QUALITÉ MAXIMALE activée:")
    print("  - Sample rate: 48kHz (au lieu de 24kHz)")
    print("  - Précision: FP32 (au lieu de FP16)")
    print("  - Batch size: 4 (optimisé pour 24GB VRAM)")
    print("  - Epoques: 120 (pour convergence optimale)")
    print()
    print("⚠️  EXIGENCES:")
    if has_gpu:
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"  - GPU avec 24 GB VRAM (vous avez: {vram_gb:.1f} GB)")
    else:
        print("  - GPU avec 24 GB VRAM (recommandé)")
    print("  - Entraînement très long (peut prendre 10-20 heures)")
    print("  - Beaucoup d'espace disque (checkpoints plus gros)")
    print()
    print("Avec 1h30 de données audio, l'entrainement peut prendre:")
    print("  - 10-20 heures sur RTX 4080 Ti (selon nombre de segments)")
    print("  - Qualité vocale: MAXIMALE (voix humaine naturelle)")
    print()

    response = input("Continuer? (oui/non): ").strip().lower()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("Annule.")
        exit(0)

    print()
    print("=" * 60)
    print("DEBUT DE L'ENTRAINEMENT")
    print("=" * 60)
    print()

    try:
        # Initialiser le modèle depuis la config
        print("Initialisation du modele...")
        model = GPTTrainer.init_from_config(config)
        print("Modele initialise!")
        print()
        
        # Créer le Trainer
        from trainer import Trainer, TrainerArgs
        
        trainer_args = TrainerArgs(
            restore_path=None,  # XTTS checkpoint est restauré via xtts_checkpoint
            skip_train_epoch=False,
            start_with_eval=False,
            grad_accum_steps=GRAD_ACUMM_STEPS,
        )
        
        trainer = Trainer(
            trainer_args,
            config,
            output_path=str(RUN_PATH),
            model=model,
            train_samples=train_samples,
            eval_samples=eval_samples,
        )
        
        # Lancer l'entraînement
        print("Lancement de l'entrainement...")
        try:
            trainer.fit()
        except Exception as fit_error:
            # Intercepter l'erreur AVANT que le trainer ne tente de supprimer le dossier
            print()
            print("=" * 60)
            print("ERREUR lors de l'entrainement")
            print("=" * 60)
            print()
            print(f"Erreur: {fit_error}")
            import traceback
            traceback.print_exc()
            print()
            print("NOTE: Le dossier de training n'a pas ete supprime automatiquement.")
            print(f"  Dossier: {RUN_PATH}")
            print("  Pour nettoyer: python cleanup_training.py")
            # Ne pas relancer l'exception - cela évite que le trainer ne tente de supprimer
            return
        
        print()
        print("=" * 60)
        print("ENTRAINEMENT TERMINE!")
        print("=" * 60)
        print()
        print(f"Modele sauvegarde dans: {RUN_PATH}")
        print()
        
    except KeyboardInterrupt:
        print()
        print("Entrainement interrompu par l'utilisateur.")
        print(f"Checkpoint sauvegarde dans: {RUN_PATH}")
    except Exception as e:
        print(f"ERREUR lors de l'entrainement: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("NOTE: Le dossier de training peut etre verrouille.")
        print("  Pour nettoyer: python cleanup_training.py")
        exit(0)

if __name__ == '__main__':
    main()