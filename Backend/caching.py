import os
import json

CACHE_DIR = "pokemon_cache"
SMOGON_CACHE_DIR = "smogon_cache"
SPRITES_CACHE_DIR = "sprites_cache"

def init_caches():
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(SMOGON_CACHE_DIR, exist_ok=True)
    os.makedirs(SPRITES_CACHE_DIR, exist_ok=True)

def get_root(root):
    if root == "smogon":
        return SMOGON_CACHE_DIR
    elif root == "pokemon":
        return CACHE_DIR
    elif root == "sprites":
        return SPRITES_CACHE_DIR
    
def load_from_cache(path):
    with open(path, 'r') as f:
        return json.load(f)
    
def load_from_smogon():
    smogon_path = f"{SMOGON_CACHE_DIR}/data_list.json"
    if not os.path.exists(smogon_path):
        return
    try:
        with open(smogon_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"error loading from cache path {smogon_path}: {e}")
        return None
        
def load_from_pokemon(pokemon):
    pokemon_path = f"{CACHE_DIR}/{pokemon}.json"
    # print(pokemon_path)
    if not os.path.exists(pokemon_path):
        # print("path does not exist")
        return None
    try:
        with open(pokemon_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"error loading from cache path {pokemon_path}: {e}")
        return None
    
def dump_gif_in_cache(path, gif):
    with open(path, "wb") as f:
        f.write(gif)
    
def dump_in_cache(path, contents):
    with open(path, "w") as f:
        json.dump(contents, f, indent=4)