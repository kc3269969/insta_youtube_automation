import moviepy.editor as mp
import os

def add_intro_outro(clip, intro_path, outro_path):
    intro = mp.VideoFileClip(intro_path).resize(clip.size)
    outro = mp.VideoFileClip(outro_path).resize(clip.size)
    return mp.concatenate_videoclips([intro, clip, outro])

def apply_edits(filename):
    processed_dir = "processed"
    os.makedirs(processed_dir, exist_ok=True)
    clip = mp.VideoFileClip(filename)
    # Example: crop, zoom, rotate
    edited = clip.crop(x1=20, y1=20, x2=clip.w-20, y2=clip.h-20).rotate(1)
    edited = add_intro_outro(edited, "assets/intro.mp4", "assets/outro.mp4")
    output = os.path.join(processed_dir, os.path.basename(filename))
    edited.write_videofile(output, codec="libx264")
    return output

def process_videos():
    for fname in os.listdir("downloads"):
        if not fname.endswith(".mp4"):
            continue
        out_path = os.path.join("processed", fname)
        if os.path.exists(out_path):
            continue
        apply_edits(os.path.join("downloads", fname))