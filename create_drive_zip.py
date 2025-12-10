import zipfile
import os
import tqdm

def create_zip(output_filename, source_dir):
    print(f"Creating {output_filename} from {source_dir}...")
    
    files_to_include = [
        'metadata.json',
        'metadata_train.csv',
        'metadata_eval.csv'
    ]
    
    folder_to_include = 'wavs'

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add metadata files
        for filename in files_to_include:
            file_path = os.path.join(source_dir, filename)
            if os.path.exists(file_path):
                print(f"Adding {filename}...")
                zipf.write(file_path, arcname=filename)
            else:
                print(f"Warning: {filename} not found!")

        # Add wavs folder
        wavs_path = os.path.join(source_dir, folder_to_include)
        if os.path.exists(wavs_path):
            print(f"Adding {folder_to_include} directory...")
            for root, dirs, files in os.walk(wavs_path):
                for file in files:
                    if file.endswith('.wav'):
                        file_path = os.path.join(root, file)
                        # Archive name should be wavs/filename.wav
                        # root is dataset_training/wavs, we want arcname to start with wavs
                        rel_path = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname=rel_path)
        else:
            print(f"Warning: {folder_to_include} directory not found!")
            
    print(f"✅ Success! {output_filename} created.")

if __name__ == "__main__":
    create_zip("darija_dataset.zip", "dataset_training")
