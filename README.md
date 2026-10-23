# hand-to-spritesheet
A python script for Windows 11 that automatically creates hand spritesheets from green/blue screen `.mp4` videos.

I've only tested this script using recordings from my Google Pixel 7 (using OpenCamera). Some tweaks may be needed for different video encodings.

## Installation
1) Clone this repo and ensure that the CorridorKey submodule is downloaded as well.
2) Install CorridorKey by double-clicking `CorridorKey/Install_CorridorKey_Windows.bat`.
3) Edit line 57 of `CorridorKey/clip_manager.py` to `CLIPS_DIR = os.path.join("../temp/")`. This is hacky, but as far as I can tell, CorridorKey doesn't have a way to specify a clips folder.
3) Install [ImageMagick](https://imagemagick.org/download/#windows) and ensure it is added to your PATH.
4) Install [ffmpeg](https://www.ffmpeg.org/download.html) and ensure it is added to your PATH.

## Running
Run `python main.py [name of video in input excluding the file extension]`. You will likely need to change some of the script's basic settings at the top of `main.py` (the chroma key color in particular). The output will be saved in the root folder.

## Fixing torch/CUDA issues
If CorridorKey fails to run because the torch version does not support CUDA on your GPU, follow these steps:

1) Delete `CorridorKey/myproject.toml`.
2) Activate CorridorKey's virtual environment
3) Install pip by running `.\CorridorKey\.venv\Scripts\python.exe -m pip install --upgrade pip`.
4) Install CUDA torch by running `.\CorridorKey\.venv\Scripts\python.exe -m  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu[whatever version your GPU needs, e.g. 130]`.