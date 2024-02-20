from PIL import Image
import os
import re

def decomp(path: str):
    sprites = {}

    with open(path, 'r') as f:
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

    dirname = '/'.join(path.strip().split('/')[:-1])
    atlas_full = Image.open(f'{dirname}/{atlas_file_name}')

    if not os.path.exists(f'{dirname}/sprites'):
        os.makedirs(f'{dirname}/sprites')

    for sprite_name, attributes in sprites.items():

        left = int(attributes['xy'].split(', ')[0])
        top = int(attributes['xy'].split(', ')[1])
        right = left + int(attributes['size'].split(', ')[0])
        bottom = top + int(attributes['size'].split(', ')[1])

        sprite = atlas_full.crop((left, top, right, bottom))

        sprite.save(f'{dirname}/sprites/{sprite_name}.png')

def rebuild(path: str):
    sprites = {}

    with open(path, 'r') as f:
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

    dirname = '/'.join(path.strip().split('/')[:-1])
    canvas = Image.new(re.sub(r'\d+', '', atlas_format), tuple(map(int, atlas_size.split(', '))), (255,255,255,0))

    for sprite_name, attributes in sprites.items():
        sprite = Image.open(f'{dirname}/sprites/{sprite_name}.png')
        canvas.paste(sprite, tuple(map(int, attributes['xy'].split(', '))))
    
    if not os.path.exists(f'{dirname}/output'):
        os.makedirs(f'{dirname}/output')

    canvas.save(f'{dirname}/output/{atlas_file_name}')

if __name__ == '__main__':
    from ui.mainwindow import MainWindow
    from PySide6.QtWidgets import QApplication
    import qdarktheme

    app = QApplication()
    qdarktheme.setup_theme('dark')
    mainwindow = MainWindow()
    mainwindow.show()
    app.exec()