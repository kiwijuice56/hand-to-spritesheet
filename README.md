# kiwi-hands
A command-line program for Windows to automatically create hand spritesheets from green screen `.mp4` videos.

## Installation
1) Clone this repo.
2) Install CorridorKey by double-clicking `CorridorKey/Install_CorridorKey_Windows.bat`.
3) Edit line 57 of `CorridorKey/clip_manager.py` to `CLIPS_DIR = os.path.join("../temp/")`. This is hacky, but as far as I can tell, CorridorKey doesn't have a way to specify a clips folder.
3) Install [ImageMagick](https://imagemagick.org/download/#windows).

## Fixing torch issues
1) Delete `CorridorKey/myproject.toml`.
2) Activate CorridorKey's virtual environment and run `.\CorridorKey\.venv\Scripts\python.exe -m pip install --upgrade pip` to install pip and `.\CorridorKey\.venv\Scripts\python.exe -m  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130` to install CUDA torch (the actual version you need will depend on your GPU).

## Running
1) Run `python main.py [name of video in input, without file extension]`