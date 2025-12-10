import json

def remove_broken_cell(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    # Looking for the cell with the specific URL that causes 404
    target_url = "https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/Utils/ASR/config.yml"
    
    new_cells = []
    removed = False
    
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if target_url in source:
                print("Found broken download cell. Removing it...")
                removed = True
                continue # Skip adding this cell to new_cells
        
        new_cells.append(cell)
    
    if removed:
        notebook['cells'] = new_cells
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
        print("Notebook modified successfully: Broken cell removed.")
    else:
        print("Warning: Broken cell not found!")

if __name__ == "__main__":
    remove_broken_cell("COLAB_NOTEBOOK_FINAL.ipynb")
