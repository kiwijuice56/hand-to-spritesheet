import subprocess
import sys
import os
import shutil
import glob

# video settings
chromakey = "0x248463"
width = 512
height = 288
fps = 12

cwd = os.getcwd()
video_path = os.path.join(cwd, "input", f"{sys.argv[1]}.mp4") 
downscaled_path = os.path.join(cwd, "temp", "video", "Input.mp4")
alpha_mask_path = os.path.join(cwd, "temp", "video", "AlphaHint", "%04d.png")
corridor_key_output_path = os.path.join(cwd, "temp", "video", "Output", "Processed", "*.exr")
final_output_path = os.path.join(cwd, f"{sys.argv[1]}_sheet.png") 

if os.path.exists("temp"):
    shutil.rmtree("temp")

os.makedirs("temp")
os.makedirs(os.path.join("temp", "video", "AlphaHint"))
os.makedirs(os.path.join("temp", "video", "VideoMamaMaskhint"))

# convert to lower fps and lower scale
subprocess.run(["ffmpeg", "-i", video_path, "-filter:v", f"scale={width}:{height},fps={fps}", downscaled_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# generate quick alpha mask with chroma key
subprocess.run(["ffmpeg", "-i", downscaled_path, "-vf", f"scale={width}:{height},colorkey={chromakey}:similarity=0.2:blend=0.1,format=rgba,alphaextract[alfa]", "-pix_fmt", "gray", 
                alpha_mask_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# use corridorkey to get clean images
subprocess.run([os.path.join(cwd, "CorridorKey", ".venv", "Scripts", "activate"), "&&", 
                "corridorkey", "run-inference", "--srgb", "--despill=5", "--no-despeckle", "--image-size=1024", "--refiner=1.0", "--no-comp", "--no-tile", "--screen-color=green"], 
                shell=True, cwd=os.path.join(cwd, "CorridorKey"))

# get bounding box to crop images
bounding_box_return = subprocess.run(["magick", corridor_key_output_path, "-background", "white", "-layers", "flatten", "-fuzz", "5%", "-trim", 
                    "-format", "\"%wx%h%O\"", "info:"], capture_output = True, text = True)
bounding_box = str(bounding_box_return.stdout)
bounding_box = bounding_box[bounding_box.find("\"") + 1 : bounding_box.rfind("\"")]

# convert exr to png, fix colors and crop
frames = b""
for exr in sorted(glob.glob(corridor_key_output_path)):
    frames += subprocess.run(["magick", exr,
                              "-channel", "RGB", "-fx", "u.a > 0 ? u/u.a : 0", "+channel",
                              "-colorspace", "sRGB", "-gamma", "2.2",
                              "-crop", bounding_box, "+repage",
                              "miff:-"], capture_output=True, check=True).stdout

# pack into spritesheet
subprocess.run(["magick", "montage", "-", "-geometry", "+0+0", "-tile", "8x",
                "-background", "none", "PNG32:" + final_output_path],
               input=frames, check=True)