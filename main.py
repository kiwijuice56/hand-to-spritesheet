import subprocess
import sys
import os
import shutil
import glob
import random

# basic settings
chroma_color = "0x2c916a" # will need to change manually each time to account for exposure differences
chroma_similarity = 0.15 # [0, 1]; lower = less of the subject is keyed out. decrease if the hand has chunks taken out 
output_scale = 0.4 # original video resolution x output scale = resolution of each frame in the spritesheet
fps = 12 

# advanced settings
chroma_blend = 0.0 # [0, 1]; how much the chroma key result is blurred. should generally be kept at 0.0 for crisp edges
inference_size = 1024 # [512, 1024, 2048]; higher = crisper results but takes longer
internal_width, internal_height = 1920, 1080 # best to keep as the size of the original video but can be downscaled for speed
refiner = 1.0 # [0, 1]; see CorridorKey for explanation because idk what this does
despill = 8 # [1, 10]; integer; removes some of the green light bounce

# paths to stuff
cwd = os.getcwd()
video_path = os.path.join(cwd, "input", f"{sys.argv[1]}.mp4") 
downscaled_path = os.path.join(cwd, "temp", "video", "Input.mp4")
alpha_mask_path = os.path.join(cwd, "temp", "video", "AlphaHint", "%04d.png")
corridor_key_output_path = os.path.join(cwd, "temp", "video", "Output", "Processed", "*.exr")
final_output_path = os.path.join(cwd, f"{sys.argv[1]}_{random.randrange(1000, 9999)}_sheet.png") 

if os.path.exists("temp"):
    shutil.rmtree("temp")
os.makedirs("temp")
os.makedirs(os.path.join("temp", "video", "AlphaHint"))
os.makedirs(os.path.join("temp", "video", "VideoMamaMaskhint"))

# convert to lower fps and lower scale
subprocess.run(["ffmpeg", "-i", video_path, 
                "-filter:v", f"scale={internal_width}:{internal_height}:flags=neighbor,fps={fps}", downscaled_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# generate quick alpha mask with chroma key
subprocess.run(["ffmpeg", "-i", downscaled_path, 
                "-vf", f"scale={internal_width}:{internal_height}:flags=neighbor,colorkey={chroma_color}:similarity={chroma_similarity}:blend={chroma_blend},format=rgba,alphaextract[alfa]", "-pix_fmt", "gray", alpha_mask_path], 
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# use corridorkey to get clean images
subprocess.run([os.path.join(cwd, "CorridorKey", ".venv", "Scripts", "activate"), "&&", 
                "corridorkey", "run-inference", 
                "--srgb", f"--despill={despill}", "--despeckle", f"--image-size={inference_size}", f"--refiner={refiner}", "--no-comp", "--no-tile", "--screen-color=auto"], 
                shell=True, cwd=os.path.join(cwd, "CorridorKey"))

# get bounding box to crop images
bounding_box_return = subprocess.run(["magick", corridor_key_output_path, 
                                      "-background", "white", "-layers", "flatten", "-trim", "-format", "\"%wx%h%O\"", "info:"],
                                      capture_output=True, text=True)
bounding_box = str(bounding_box_return.stdout)
bounding_box = bounding_box[bounding_box.find("\"") + 1 : bounding_box.rfind("\"")]

# convert exr to png, fix alpha/colors then crop
frames = b""
for exr in sorted(glob.glob(corridor_key_output_path)):
    frames += subprocess.run(["magick", exr,
                              "-channel", "RGB", "-fx", "u.a > 0 ? u/u.a : 0", "+channel",
                              "-colorspace", "sRGB", "-gamma", "2.2",
                              "-crop", bounding_box, "+repage", "miff:-"],
                              capture_output=True, check=True).stdout

# pack into spritesheet
subprocess.run(["magick", "montage", "-", "-geometry", "+0+0", "-tile", "16x",
                "-background", "none", "-filter", "point", "-scale", f"%{output_scale * 100}", "PNG32:" + final_output_path],
               input=frames, check=True)

print("All done, output image:", final_output_path)