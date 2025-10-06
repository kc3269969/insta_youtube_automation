import os
import moviepy.editor as mp
from moviepy.video.fx.all import crop
from utils import log_message

# NOTE: Intro/Outro files must be available in the path specified in .env
# Example paths: env['INTRO_VIDEO_PATH'], env['OUTRO_VIDEO_PATH']

def process_video(download_path, env):
    """Applies edits: intro/outro, slight crop/zoom, and saves to /processed/."""
    try:
        # Load clips
        main_clip = mp.VideoFileClip(download_path)
        
        # 1. Apply slight transformation (Zoom/Crop for uniqueness)
        w, h = main_clip.size
        # Simple slight zoom: 95% of original size, centered
        new_w, new_h = w * 0.95, h * 0.95
        cropped_clip = crop(main_clip, width=new_w, height=new_h, x_center=w/2, y_center=h/2)
        
        # 2. Add Intro/Outro (if paths are provided)
        final_clip = cropped_clip
        clips_to_concat = [final_clip]
        
        if 'INTRO_VIDEO_PATH' in env and os.path.exists(env['INTRO_VIDEO_PATH']):
            intro_clip = mp.VideoFileClip(env['INTRO_VIDEO_PATH']).resize(cropped_clip.size)
            clips_to_concat.insert(0, intro_clip)
            log_message("INFO", "Added intro.")

        if 'OUTRO_VIDEO_PATH' in env and os.path.exists(env['OUTRO_VIDEO_PATH']):
            outro_clip = mp.VideoFileClip(env['OUTRO_VIDEO_PATH']).resize(cropped_clip.size)
            clips_to_concat.append(outro_clip)
            log_message("INFO", "Added outro.")
        
        # Concatenate all clips
        if len(clips_to_concat) > 1:
            final_clip = mp.concatenate_videoclips(clips_to_concat)
            
        # 3. Optional Background Music (Example: lowers volume of main audio and adds separate track)
        # if music_file_path:
        #     music_clip = mp.AudioFileClip(music_file_path).volumex(0.3)
        #     final_clip = final_clip.set_audio(music_clip.set_duration(final_clip.duration))

        # 4. Save processed file
        base_name = os.path.basename(download_path)
        output_filename = f"processed_{base_name}"
        output_path = os.path.join(env['PROCESS_DIR'], output_filename)
        
        # Write the video file with appropriate codec for Shorts (H.264)
        final_clip.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac', 
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True,
            logger=None # Suppress moviepy logs
        )

        log_message("INFO", f"Successfully processed video: {output_path}")
        return output_path

    except Exception as e:
        log_message("ERROR", f"Video processing failed for {download_path}: {e}")
        return None
