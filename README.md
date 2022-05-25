# Image Spell

## Topics
  * [About](#about)
  * [Packages](#packages)
  * [Installation](#installation)
  * [Supported Image Formats](#supported-image-formats)
  * [Shortcuts and Features](#shortcuts-and-features)
  * [License](#license)

## About
This is an ***image manipulation program*** made with **Python 3**

#### See a [preview](https://youtu.be/n0BW8PmxzyQ)
## Packages
- [NumPy](https://pypi.org/project/numpy/)
- [PySide6](https://pypi.org/project/PySide6/)
- [Pillow](https://pypi.org/project/Pillow/)

## Installation
#### Install [Python](https://www.python.org/downloads/), and download this repo before the following commands in terminal:
```sh
# Inside the repo directory
# Install required packages
pip install -r requirements.txt
# Compile UI
./setup.sh
# Execute program
python main.py
```

## Supported image formats
|Format |Description                      |Support    |
|:-----:|:-------------------------------:|:---------:|
|JPG    |Joint Photographic Experts Group |Read/Write |
|JPEG   |Joint Photographic Experts Group |Read/Write |
|PNG    |Portable Network Graphics        |Read/Write |
|BMP    |Windows Bitmap                   |Read/Write |
|PPM    |Portable Pixmap                  |Read/Write |
|GIF    |Graphic Interchange Format       |Read-Only  |
|PBM    |Portable Bitmap                  |Read-Only  |
|PGM    |Portable Graymap                 |Read-Only  |
#### Support other file types depends on 3rd-part softwares, it's a coming soon feature...

## Shortcuts and features
|Shortcut                     |Action                           |
|----------------------------:|:--------------------------------|
|**Ctrl** + **O**             |Open File                        |
|**Ctrl** + **S**             |Save File                        |
|**Ctrl** + **Shift** + **S** |Save File As                     |
|**Ctrl** + **R**             |Resize Image                     |
|**Ctrl** + **T**             |Toogle Fit in view / Normal size |
|**Ctrl** + **+**             |Zoom In                          |
|**Ctrl** + **-**             |Zoom Out                         |
|**Ctrl** + **Z**             |Undo changes                     |
|**Ctrl** + **Shift** + **Z** |Redo changes                     |
|**Ctrl** + **I**             |Show image information           |
|**Ctrl** + **'**             |Set settings                     |
|**Ctrl** + **A**             |Show about                       |
|**Ctrl** + **E**             |Exit                             |
|Hold **Ctrl**                |Mouse Wheel Zoom Mode            |
|Hold **Shift**               |Mouse Drag Navigation Mode       |
|Press **F11**                |Toggle Fullscreen                |

## License
[MIT](https://opensource.org/licenses/MIT)
