from PIL import Image
import pathlib


class Atlas():
    def __init__(self, atlas_path: pathlib.Path, img_name: str, img_size: str, img_format: str, img_filter: str, repeat: str):
        self.atlas_path = atlas_path
        self.img_name = img_name
        self.img_size = img_size
        self.img_format = img_format
        self.img_filter = img_filter
        self.repeat = repeat
        self.sprites = {}
    
    def add_sprite(self, name, attributes):
        self.sprites[name] = attributes

    def get_sprites(self) -> dict:
        return self.sprites
    

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