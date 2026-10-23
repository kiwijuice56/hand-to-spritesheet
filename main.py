import subprocess
import sys
import os
import shutil

# import CorridorKey.corridorkey_cli as ck

# video settings
chromakey = "0x248463"
width = 1280 / 2.
height = 720 / 2.
fps = 12

cwd = os.getcwd()
video_path = os.path.join(cwd, "input", f"{sys.argv[1]}.mp4") 
fixed_fps_path = os.path.join(cwd, "temp", "video", "Input.mp4")
alpha_mask_path = os.path.join(cwd, "temp", "video", "AlphaHint", "%04d.png")

if os.path.exists("temp"):
    shutil.rmtree("temp")

os.makedirs("temp")
os.makedirs(os.path.join("temp", "video", "AlphaHint"))
os.makedirs(os.path.join("temp", "video", "VideoMamaMaskhint"))

try: 
    # convert to lower fps and lower scale
    subprocess.run(["ffmpeg", "-i", video_path, "-filter:v", f"scale={width}:{height},fps={fps}", fixed_fps_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # generate quick alpha mask with chroma key
    subprocess.run(["ffmpeg", "-i", fixed_fps_path, "-vf", f"scale={width}:{height},colorkey={chromakey}:similarity=0.2:blend=0.1,format=rgba,alphaextract[alfa]", "-pix_fmt", "gray", 
                    alpha_mask_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # use corridorkey to get clean images
    subprocess.run([os.path.join(cwd, "CorridorKey", ".venv", "Scripts", "activate"), "&&", 
                    "corridorkey", "run-inference", "--srgb", "--despill=5", "--no-despeckle", "--image-size=512", "--refiner=1.0", "--no-comp", "--no-tile", "--screen-color=green"], 
                    shell=True, cwd=os.path.join(cwd, "CorridorKey"))

    # chroma key out
    #ck.interactive_wizard(win_path=fixed_fps_path, device="cuda")

finally:
    pass
    #shutil.rmtree("temp")