from PIL import Image
import pathlib
import hashlib
from collections import Counter


class Atlas():
    def __init__(self, atlas_path: pathlib.Path, img_name: str, img_size: str, img_format: str, img_filter: str, repeat: str):
        self.atlas_path = atlas_path
        self.img_name = img_name
        self.img_size = img_size
        self.img_format = img_format
        self.img_filter = img_filter
        self.repeat = repeat
        self.sprites = {}
        self.sprite_hashes = {}
    
    def add_sprite(self, name, attributes):
        self.sprites[name] = attributes

    def get_sprites(self) -> dict:
        return self.sprites
    
    def add_sprite_hash(self, name, hash):
        self.sprite_hashes[name] = hash

def get_atlas(path: pathlib.Path) -> Atlas:
    t = path.read_text().strip().split('\n')

    atlas = Atlas(path.absolute(), *[ t.strip().split(': ')[1] if ': ' in t else t for t in t[:5] ])

    for line in t[5:]:
        line = line.strip()

        if ':' not in line:
            sprite_name = line
            attributes = {}
        else:
            name, value = line.strip().split(': ')
            attributes[name] = value

            if name == 'index':
                if int(value) >= 0:
                    sprite_name = f'{sprite_name}_{value}'

                atlas.add_sprite(sprite_name, attributes)

    return atlas

def get_image_hash(image_path: pathlib.Path) -> str:
    with open(image_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def decomp(atlas: Atlas):
    atlas_dir = atlas.atlas_path.parent
    atlas_img = Image.open(atlas_dir / atlas.img_name)
    sprites_dir = atlas_dir / 'sprites'
    sprites_dir.mkdir(exist_ok=True)
    
    for sprite_name, attributes in atlas.get_sprites().items():

        left = int(attributes['xy'].split(', ')[0])
        top = int(attributes['xy'].split(', ')[1])
        right = left + int(attributes['size'].split(', ')[0])
        bottom = top + int(attributes['size'].split(', ')[1])

        sprite = atlas_img.crop((left, top, right, bottom))

        sprite.save(sprites_dir / f'{sprite_name}.png')
        atlas.add_sprite_hash(sprite_name, get_image_hash(sprites_dir / f'{sprite_name}.png'))

def find_duplicates(atlas: Atlas) -> list:
    sprites = atlas.get_sprites()

    attributes = sprites.values()
    coord_counts = Counter(d['xy'] for d in attributes)
    duplicate_coords = {coord for coord,
                        count in coord_counts.items() if count > 1}

    result = [sprite_name for sprite_name,
              d in sprites.items() if d['xy'] in duplicate_coords]

    return result

def check_duplicates(atlas: Atlas):
    atlas_dir = atlas.atlas_path.parent
    sprites_dir = atlas_dir / 'sprites'
    duplicates = find_duplicates(atlas)

    modified_dupe_sprites = []

    for sprite_name, attributes in atlas.get_sprites().items():
        if atlas.sprite_hashes[sprite_name] != get_image_hash(sprites_dir / f'{sprite_name}.png'):
            if sprite_name in duplicates:
                modified_dupe_sprites.append((sprite_name, attributes))

    for sprite_name, attributes in modified_dupe_sprites:

        atlas.get_sprites().pop(sprite_name)
        atlas.add_sprite(sprite_name, attributes)

        removed_hash = atlas.sprite_hashes.pop(sprite_name)
        atlas.add_sprite_hash(sprite_name, removed_hash)
        
def rebuild(atlas: Atlas):
    canvas = Image.new('RGBA', tuple(map(int, atlas.img_size.split(', '))), (255,255,255,0))

    for sprite_name, attributes in atlas.get_sprites().items():
        sprite = Image.open(atlas.atlas_path.parent / 'sprites' / f'{sprite_name}.png')
        canvas.paste(sprite, tuple(map(int, attributes['xy'].split(', '))))
    
    output_dir = atlas.atlas_path.parent / 'output'
    output_dir.mkdir(exist_ok=True)

    canvas.save(output_dir / atlas.img_name)

if __name__ == '__main__':
    from ui.mainwindow import MainWindow
    from PySide6.QtWidgets import QApplication
    import qdarktheme

    app = QApplication()
    qdarktheme.setup_theme('dark')
    mainwindow = MainWindow()
    mainwindow.show()
    app.exec()