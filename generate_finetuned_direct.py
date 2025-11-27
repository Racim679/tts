#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer de l'audio avec le modèle XTTS fine-tuné DIRECTEMENT
Utilise le checkpoint sauvegardé dans xtts_finetuned/run/training

Usage:
    python generate_finetuned_direct.py                    # Mode interactif
    python generate_finetuned_direct.py --pls file.pls     # Générer depuis un fichier PLS
    python generate_finetuned_direct.py --file texts.txt   # Générer depuis un fichier texte
"""

import sys
import os
import argparse
from pathlib import Path

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import torch
import soundfile as sf

def parse_pls_file(pls_path):
    """Parse un fichier PLS et retourne une liste de textes"""
    texts = []
    with open(pls_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('[') or line.startswith('#'):
            continue
        # Format PLS: File1=texte ou juste le texte
        if '=' in line:
            # Extraire le texte après le =
            text = line.split('=', 1)[1].strip()
            if text:
                texts.append(text)
        else:
            # Ligne simple avec texte
            if line:
                texts.append(line)
    
    return texts

def parse_text_file(text_path):
    """Parse un fichier texte simple (une ligne = un texte)"""
    texts = []
    with open(text_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                texts.append(line)
    return texts

def find_latest_checkpoint(training_dir):
    """Trouve le checkpoint le plus récent"""
    training_path = Path(training_dir)
    if not training_path.exists():
        return None, None
    
    # Chercher les dossiers de training
    training_folders = [d for d in training_path.iterdir() if d.is_dir() and d.name.startswith("XTTS_Darija_FT")]
    if not training_folders:
        return None, None
    
    # Prendre le plus récent
    latest_folder = max(training_folders, key=lambda x: x.stat().st_mtime)
    
    # Chercher best_model.pth (le meilleur checkpoint)
    best_model = latest_folder / "best_model.pth"
    if best_model.exists():
        return best_model, latest_folder
    
    # Sinon, chercher d'autres checkpoints
    checkpoint_files = list(latest_folder.glob("*.pth"))
    if not checkpoint_files:
        return None, None
    
    # Prendre le checkpoint le plus récent
    latest_checkpoint = max(checkpoint_files, key=lambda x: x.stat().st_mtime)
    return latest_checkpoint, latest_folder

def generate_audio_for_text(model, synth_config, reference_audio, text, output_file, max_recommended=166, max_absolute=200):
    """Génère l'audio pour un texte donné"""
    # Vérifier la limite de caractères
    text_length = len(text)
    
    if text_length > max_absolute:
        print(f"  ⚠️  ATTENTION: Texte trop long ({text_length} > {max_absolute})")
        print(f"     Le texte sera tronque a {max_absolute} caracteres")
        text = text[:max_absolute]
        text_length = len(text)
    elif text_length > max_recommended:
        print(f"  ⚠️  AVERTISSEMENT: Texte assez long ({text_length} > {max_recommended})")
        print(f"     La qualite peut etre degradee. Limite recommandee: {max_recommended} caracteres")
    else:
        print(f"  ✓ Longueur OK ({text_length} caracteres)")
    
    print()
    print(f"  Generation en cours...")
    print(f"  Texte: {text[:80]}..." if len(text) > 80 else f"  Texte: {text}")
    print(f"  Reference: {reference_audio}")
    print(f"  Output: {output_file}")
    print("  (Cela peut prendre 30-60 secondes)")
    print()
    
    try:
        print("    Generation de l'audio en cours...")
        with torch.no_grad():
            result = model.xtts.synthesize(
                text,
                synth_config,
                [reference_audio],
                "ar",
                gpt_cond_len=3,
            )
            wav = result["wav"]
        print("    Audio genere!")
        
        # Convertir et sauvegarder
        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()
        
        if len(wav.shape) > 1:
            wav = wav[0]
        
        output_sr = synth_config.audio.output_sample_rate if hasattr(synth_config, 'audio') and hasattr(synth_config.audio, 'output_sample_rate') else 24000
        sf.write(output_file, wav, output_sr)
        
        file_size = os.path.getsize(output_file) / 1024
        print(f"    ✓ Fichier sauvegarde: {output_file} ({file_size:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"    ✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    # Parser d'arguments
    parser = argparse.ArgumentParser(description='Générer de l\'audio avec le modèle XTTS fine-tuné')
    parser.add_argument('--pls', type=str, help='Fichier PLS contenant les textes à générer')
    parser.add_argument('--file', type=str, help='Fichier texte (une ligne = un texte)')
    parser.add_argument('--output-dir', type=str, default='outputs', help='Dossier de sortie (défaut: outputs)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Generation Audio avec Modele Fine-tune XTTS-v2 (DIRECT)")
    print("=" * 60)
    print()
    
    # Vérifier GPU
    has_gpu = torch.cuda.is_available()
    device = "cuda" if has_gpu else "cpu"
    print(f"Device: {device}")
    if has_gpu:
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print()
    
    # Trouver le checkpoint fine-tuné
    training_dir = Path("xtts_finetuned/run/training")
    checkpoint_path, checkpoint_dir = find_latest_checkpoint(training_dir)
    
    if not checkpoint_path:
        print("ERREUR: Aucun checkpoint fine-tune trouve!")
        print(f"  Cherche dans: {training_dir}")
        exit(1)
    
    print(f"Checkpoint fine-tune trouve:")
    print(f"  Fichier: {checkpoint_path.name}")
    print(f"  Dossier: {checkpoint_dir}")
    print()
    
    # Charger la config
    print("Chargement de la configuration...")
    from TTS.tts.configs.xtts_config import XttsConfig
    
    config_file = checkpoint_dir / "config.json"
    if not config_file.exists():
        print(f"ERREUR: Fichier config.json non trouve dans {checkpoint_dir}")
        exit(1)
    
    config = XttsConfig()
    config.load_json(str(config_file))
    print("  Config chargee!")
    print()
    
    # Charger les fichiers nécessaires du modèle original
    print("Chargement des fichiers du modele de base...")
    model_files_dir = training_dir / "XTTS_v2.0_original_model_files"
    
    if not model_files_dir.exists():
        print(f"ERREUR: Dossier des fichiers du modele non trouve: {model_files_dir}")
        exit(1)
    
    dvae_checkpoint = model_files_dir / "dvae.pth"
    mel_norm_file = model_files_dir / "mel_stats.pth"
    tokenizer_file = model_files_dir / "vocab.json"
    
    if not all([dvae_checkpoint.exists(), mel_norm_file.exists(), tokenizer_file.exists()]):
        print(f"ERREUR: Fichiers du modele de base manquants dans {model_files_dir}")
        exit(1)
    
    print("  Fichiers du modele de base trouves!")
    print()
    
    # Initialiser le modèle
    print("Initialisation du modele fine-tune...")
    print("  (Cela peut prendre 1-2 minutes)")
    print()
    
    try:
        from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTTrainer, GPTArgs, XttsAudioConfig
        
        # Créer les arguments du modèle (valeurs par défaut)
        model_args = GPTArgs(
            max_conditioning_length=132300,  # 6 secs
            min_conditioning_length=66150,  # 3 secs
            debug_loading_failures=False,
            max_wav_length=255995,  # ~11.6 seconds
            max_text_length=200,
            mel_norm_file=str(mel_norm_file),
            dvae_checkpoint=str(dvae_checkpoint),
            xtts_checkpoint=str(model_files_dir / "model.pth"),
            tokenizer_file=str(tokenizer_file),
            gpt_num_audio_tokens=1026,
            gpt_start_audio_token=1024,
            gpt_stop_audio_token=1025,
            gpt_use_masking_gt_prompt_approach=True,
            gpt_use_perceiver_resampler=True,
        )
        
        audio_config = XttsAudioConfig(
            sample_rate=22050,
            dvae_sample_rate=22050,
            output_sample_rate=24000
        )
        
        # Créer la config de trainer
        from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTTrainerConfig
        trainer_config = GPTTrainerConfig()
        trainer_config.load_json(str(config_file))
        trainer_config.model_args = model_args
        trainer_config.audio = audio_config
        
        # Initialiser le modèle depuis la config
        model = GPTTrainer.init_from_config(trainer_config)
        
        # Charger le checkpoint fine-tuné
        print("  Chargement du checkpoint fine-tune...")
        checkpoint_dict = torch.load(checkpoint_path, map_location=device)
        
        # Le checkpoint du trainer contient les poids dans 'model' avec préfixe 'xtts.'
        if 'model' in checkpoint_dict:
            model_state = checkpoint_dict['model']
            print(f"  Format detecte: checkpoint trainer (clé 'model')")
            print(f"  Nombre de poids: {len(model_state)}")
            
            # Compter les poids GPT fine-tunés
            gpt_keys = [k for k in model_state.keys() if 'gpt' in k.lower()]
            print(f"  Poids GPT fine-tunes: {len(gpt_keys)}")
            
            # Charger tous les poids (incluant les poids GPT fine-tunés)
            # Les clés ont le préfixe 'xtts.' donc on peut charger directement
            missing_keys, unexpected_keys = model.load_state_dict(model_state, strict=False)
            
            if missing_keys:
                print(f"  ⚠️  Poids manquants: {len(missing_keys)} (normal si certains poids ne sont pas dans le checkpoint)")
            if unexpected_keys:
                print(f"  ⚠️  Poids inattendus: {len(unexpected_keys)} (normal si le checkpoint contient des poids supplémentaires)")
            
            # Vérifier que les poids GPT ont été chargés
            if gpt_keys:
                print(f"  ✓ Poids GPT fine-tunes charges: {len(gpt_keys)} poids")
            else:
                print("  ⚠️  ATTENTION: Aucun poids GPT trouve dans le checkpoint!")
                
        elif 'gpt' in checkpoint_dict:
            print("  Format detecte: checkpoint avec clé 'gpt' directe")
            model.xtts.gpt.load_state_dict(checkpoint_dict['gpt'], strict=False)
            print("  ✓ Poids GPT charges")
        else:
            print("  Format detecte: state_dict direct")
            missing_keys, unexpected_keys = model.load_state_dict(checkpoint_dict, strict=False)
            if missing_keys:
                print(f"  ⚠️  Poids manquants: {len(missing_keys)}")
            if unexpected_keys:
                print(f"  ⚠️  Poids inattendus: {len(unexpected_keys)}")
        
        model.to(device)
        model.eval()
        
        print("  Modele fine-tune charge avec succes!")
        print("  ⚠️  IMPORTANT: Assurez-vous d'utiliser un audio de reference de votre dataset!")
        print()
        
    except Exception as e:
        print(f"ERREUR lors du chargement du modele: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    # Fichier audio de référence
    # IMPORTANT: Utiliser un audio du dataset d'entraînement pour avoir la bonne voix
    reference_audio = "reference.wav"
    if not os.path.exists(reference_audio):
        dataset_ref = Path("dataset_training/wavs")
        if dataset_ref.exists():
            ref_files = list(dataset_ref.glob("*.wav"))
            if ref_files:
                reference_audio = str(ref_files[0])
                print(f"Audio de reference (depuis dataset): {reference_audio}")
                print(f"  ✓ Utilisation d'un fichier du dataset d'entrainement")
            else:
                print(f"ERREUR: Aucun fichier audio trouve dans dataset_training/wavs")
                exit(1)
        else:
            print(f"ERREUR: Dossier dataset_training/wavs non trouve")
            exit(1)
    else:
        print(f"Audio de reference: {reference_audio}")
        print(f"  ⚠️  ATTENTION: Assurez-vous que cet audio vient de votre dataset d'entrainement!")
    
    print()
    
    # Initialiser pour l'inference (une seule fois)
    print("Initialisation pour l'inference...")
    print("  Initialisation GPT...")
    model.xtts.gpt.init_gpt_for_inference(kv_cache=True, use_deepspeed=False)
    model.xtts.gpt.eval()
    print("  GPT initialise!")
    
    # Créer une config XttsConfig pour la synthèse
    print("  Chargement de la config de synthese...")
    synth_config = XttsConfig()
    synth_config.load_json(str(model_files_dir / "config.json"))
    print("  Config chargee!")
    print()
    
    # Récupérer les textes à générer
    texts_to_generate = []
    
    if args.pls:
        # Mode fichier PLS
        pls_path = Path(args.pls)
        if not pls_path.exists():
            print(f"ERREUR: Fichier PLS non trouve: {pls_path}")
            exit(1)
        print(f"Lecture du fichier PLS: {pls_path}")
        texts_to_generate = parse_pls_file(pls_path)
        print(f"  {len(texts_to_generate)} textes trouves")
        
    elif args.file:
        # Mode fichier texte
        text_path = Path(args.file)
        if not text_path.exists():
            print(f"ERREUR: Fichier texte non trouve: {text_path}")
            exit(1)
        print(f"Lecture du fichier texte: {text_path}")
        texts_to_generate = parse_text_file(text_path)
        print(f"  {len(texts_to_generate)} textes trouves")
        
    else:
        # Mode interactif
        print("Texte a generer (en Darija):")
        print("  (Appuyez sur Entree pour utiliser le texte par defaut)")
        print("  (Ou entrez votre texte et appuyez sur Entree)")
        try:
            user_text = input("  > ").strip()
        except KeyboardInterrupt:
            print("\n  Annule par l'utilisateur")
            exit(0)
        except Exception as e:
            print(f"  Erreur lors de la saisie: {e}")
            user_text = ""
        
        if not user_text:
            texts_to_generate = ["السلام عليكم خاوتنا العزاز، كيفاش راكم؟ مرحبا بكم معنا اليوم."]
            print(f"  Utilisation du texte par defaut")
        else:
            texts_to_generate = [user_text]
            print(f"  Texte recu: {len(user_text)} caracteres")
    
    if not texts_to_generate:
        print("ERREUR: Aucun texte a generer!")
        exit(1)
    
    print()
    
    # Créer le dossier de sortie si nécessaire
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    max_recommended = 166
    max_absolute = 200
    
    # Générer l'audio pour chaque texte
    success_count = 0
    failed_count = 0
    
    for i, text in enumerate(texts_to_generate, 1):
        print("=" * 60)
        print(f"GENERATION {i}/{len(texts_to_generate)}")
        print("=" * 60)
        print()
        
        # Nom du fichier de sortie
        if len(texts_to_generate) == 1:
            output_file = str(output_dir / "output_finetuned_direct.wav")
        else:
            # Nom basé sur le numéro
            output_file = str(output_dir / f"output_{i:03d}.wav")
        
        if generate_audio_for_text(model, synth_config, reference_audio, text, output_file, max_recommended, max_absolute):
            success_count += 1
        else:
            failed_count += 1
        
        print()
    
    # Résumé
    print("=" * 60)
    print("RESUME")
    print("=" * 60)
    print()
    print(f"Textes generes avec succes: {success_count}/{len(texts_to_generate)}")
    if failed_count > 0:
        print(f"Echecs: {failed_count}")
    print(f"Dossier de sortie: {output_dir.absolute()}")
    print()
    print("C'est votre modele FINE-TUNE qui a genere ces audios!")

if __name__ == '__main__':
    main()
