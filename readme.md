Pokatlas
==========  

<img alt='pokatlas_img' width=600 src='https://github.com/Seth-Revz/Pokatlas/blob/main/.github/pokatlas.png'>  

Pokatlas is python desktop application for decompiling the main.atlas and main.png spritesheet used in [PokeMMO themes](https://forums.pokemmo.com/index.php?/forum/33-client-customization/) into separate sprites, allowing for easy replacement of the sprites, and recompiling the main.png image using the new sprites.  
You can choose to export as a new main.png atlas image or export as a complete importable mod.

Pokatlas was created to save time updating the atlas file after each game update.

## Requirements  

- [Python](https://www.python.org/downloads/)  
- [PySide6](https://pypi.org/project/PySide6/)  
- [PyQtDarkTheme](https://pypi.org/project/pyqtdarktheme/)  
- [Pillow](https://pypi.org/project/pillow/)  

## Getting Started  

Clone the source code with `git` or download it as a .zip file.  

```bash
git clone https://github.com/Seth-Revz/Pokatlas.git
cd Pokatlas
pip install -r requirements.txt --ignore-requires-python
python pokatlas.py
```  
