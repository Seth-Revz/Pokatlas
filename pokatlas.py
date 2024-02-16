from PIL import Image
import os
import re

def decomp(dirname: str):
    sprites = {}

    with open(f'atlas/{dirname}/main.atlas', 'r') as f:
        _ = f.readline().strip()
        atlas_file_name = f.readline().strip()
        atlas_size = f.readline().split(': ')[1].strip()
        atlas_format = f.readline().split(': ')[1].strip()
        atlas_filter = f.readline().split(': ')[1].strip()
        atlas_repeat = f.readline().split(': ')[1].strip()
        placeholder = False

        for line in f.readlines():
            line = line.strip()
            if ':' not in line:
                sprite_name = line
                if sprite_name in sprites.keys():
                    key = f'{sprite_name}placeholder'
                    sprites[key] = {}
                    placeholder = True
                else:
                    key = sprite_name
                    sprites[key] = {}
            else:
                name, value = line.strip().split(': ')
                sprites[key][name] = value
                if placeholder and name == 'index':
                    sprites[f'{sprite_name}_INDEX{value}'] = sprites.pop(key)
                    placeholder = False

    atlas_full = Image.open(f'atlas/{dirname}/{atlas_file_name}')

    if not os.path.exists(f'atlas/{dirname}/sprites'):
        os.makedirs(f'atlas/{dirname}/sprites')

    for sprite_name, attributes in sprites.items():

        left = int(attributes['xy'].split(', ')[0])
        top = int(attributes['xy'].split(', ')[1])
        right = left + int(attributes['size'].split(', ')[0])
        bottom = top + int(attributes['size'].split(', ')[1])

        sprite = atlas_full.crop((left, top, right, bottom))

        sprite.save(f'atlas/{dirname}/sprites/{sprite_name}.png')

def rebuild(dirname: str, use_modified=False):
    sprites = {}

    with open(f'atlas/{dirname}/main.atlas', 'r') as f:
        _ = f.readline().strip()
        atlas_file_name = f.readline().strip()
        atlas_size = f.readline().split(': ')[1].strip()
        atlas_format = f.readline().split(': ')[1].strip()
        atlas_filter = f.readline().split(': ')[1].strip()
        atlas_repeat = f.readline().split(': ')[1].strip()
        placeholder = False

        for line in f.readlines():
            line = line.strip()
            if ':' not in line:
                sprite_name = line
                if sprite_name in sprites.keys():
                    key = f'{sprite_name}placeholder'
                    sprites[key] = {}
                    placeholder = True
                else:
                    key = sprite_name
                    sprites[key] = {}
            else:
                name, value = line.strip().split(': ')
                sprites[key][name] = value
                if placeholder and name == 'index':
                    sprites[f'{sprite_name}_INDEX{value}'] = sprites.pop(key)
                    placeholder = False

    canvas = Image.new(re.sub(r'\d+', '', atlas_format), tuple(map(int, atlas_size.split(', '))), (255,255,255,0))

    for sprite_name, attributes in sprites.items():
        if use_modified and os.path.exists(f'atlas/modified_sprites/{sprite_name}.png'):
            sprite = Image.open(f'atlas/modified_sprites/{sprite_name}.png')
        else:
            sprite = Image.open(f'atlas/{dirname}/sprites/{sprite_name}.png')
        canvas.paste(sprite, tuple(map(int, attributes['xy'].split(', '))))
    
    if not os.path.exists(f'atlas/{dirname}/reconstructed'):
        os.makedirs(f'atlas/{dirname}/reconstructed')

    canvas.save(f'atlas/{dirname}/reconstructed/{atlas_file_name}')

if __name__ == '__main__':
    # dirs = [ d.name for d in os.scandir(f'atlas') if d.is_dir() and d.name != 'modified_sprites']
    # for dir in dirs:
    #     decomp(dir)

    # decomp('default')
    # rebuild('default', use_modified=True)

    from ui.mainwindow import MainWindow
    from PySide6.QtWidgets import QApplication
    import qdarktheme

    app = QApplication()
    qdarktheme.setup_theme('dark')
    mainwindow = MainWindow()
    mainwindow.show()
    app.exec()