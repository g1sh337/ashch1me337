# convert_audio.py - Convert MP3 to OGG for web compatibility
import os
from pydub import AudioSegment

def convert_mp3_to_ogg(mp3_path):
    """Convert MP3 file to OGG format"""
    if not os.path.exists(mp3_path):
        print(f"File not found: {mp3_path}")
        return False
    
    ogg_path = mp3_path.replace('.mp3', '.ogg')
    
    try:
        print(f"Converting {mp3_path} to OGG...")
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(ogg_path, format="ogg", bitrate="128k")
        print(f"✅ Created: {ogg_path}")
        return True
    except Exception as e:
        print(f"❌ Error converting {mp3_path}: {e}")
        return False

if __name__ == "__main__":
    mp3_files = [
        "assets/game_music.mp3",
        "assets/menu_music.mp3"
    ]
    
    for mp3_file in mp3_files:
        convert_mp3_to_ogg(mp3_file)
    
    print("\n✨ Audio conversion complete!")
