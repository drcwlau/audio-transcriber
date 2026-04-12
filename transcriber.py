import os
import sys
import subprocess

def transcribe_audio_whisper(file_path, language='zh', model='tiny'):
    """Transcribe using OpenAI Whisper - TINY model for speed"""
    
    try:
        print(f"Using Whisper model: {model}")
        result = subprocess.run(
            ['whisper', file_path, 
             '--model', model,
             '--output_format', 'txt', 
             '--output_dir', '.', 
             '--language', language],
            capture_output=True,
            text=True,
            timeout=1800
        )
        
        if result.returncode == 0:
            print(f"✅ Transcription completed successfully")
            print(result.stdout)
            return True
        else:
            print(f"❌ Whisper error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Transcription timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main(audio_file_path, language='zh'):
    if not os.path.exists(audio_file_path):
        print("Error: Audio file does not exist.")
        return

    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    print(f"📁 File size: {file_size_mb:.2f} MB")
    print("🎙️  Processing with Whisper TINY model (fastest)...")
    
    success = transcribe_audio_whisper(audio_file_path, language=language, model='tiny')
    
    if success:
        print("✅ Transcription saved!")
    else:
        print("❌ Transcription failed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = 'path_to_your_audio_file'
    
    main(audio_file, language='zh')
