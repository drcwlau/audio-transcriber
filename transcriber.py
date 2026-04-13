import os
import sys
import subprocess
from pydub import AudioSegment

def compress_audio(file_path, output_path, target_bitrate='64k'):
    """Compress audio to reduce file size and speed up transcription"""
    print(f"🔄 Compressing audio to {target_bitrate}...")
    try:
        audio = AudioSegment.from_file(file_path)
        # Export with reduced bitrate
        audio.export(output_path, format='mp3', bitrate=target_bitrate)
        
        original_size = os.path.getsize(file_path) / (1024 * 1024)
        compressed_size = os.path.getsize(output_path) / (1024 * 1024)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        print(f"✅ Compressed: {original_size:.2f}MB → {compressed_size:.2f}MB ({reduction:.1f}% reduction)")
        return output_path
    except Exception as e:
        print(f"⚠️  Compression failed: {e}, using original file")
        return file_path

def transcribe_audio_whisper(file_path, language='zh', model='tiny'):
    """Transcribe using OpenAI Whisper - TINY model for speed"""
    
    try:
        print(f"🎙️  Using Whisper model: {model}")
        result = subprocess.run(
            ['whisper', file_path, 
             '--model', model,
             '--output_format', 'txt', 
             '--output_dir', '.', 
             '--language', language,
             '--verbose', 'False'],
            capture_output=True,
            text=True,
            timeout=3600
        )
        
        if result.returncode == 0:
            print(f"✅ Transcription completed successfully")
            return True
        else:
            print(f"❌ Whisper error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Transcription timed out after 1 hour")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main(audio_file_path, language='zh'):
    if not os.path.exists(audio_file_path):
        print("❌ Error: Audio file does not exist.")
        return

    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    print(f"📁 Original file size: {file_size_mb:.2f} MB")
    
    # Compress if file is larger than 10MB
    if file_size_mb > 10:
        print("⚡ File is large, compressing for faster processing...")
        # For very large files, use lower bitrate
        if file_size_mb > 50:
            compressed_file = compress_audio(audio_file_path, 'temp_compressed.mp3', target_bitrate='32k')
        else:
            compressed_file = compress_audio(audio_file_path, 'temp_compressed.mp3', target_bitrate='64k')
        
        transcribe_file = compressed_file
    else:
        print("✅ File size is good, no compression needed")
        transcribe_file = audio_file_path
    
    print("🎙️  Processing with Whisper TINY model (fastest)...")
    success = transcribe_audio_whisper(transcribe_file, language=language, model='tiny')
    
    # Clean up compressed file
    if transcribe_file != audio_file_path and os.path.exists(transcribe_file):
        os.remove(transcribe_file)
        print("🧹 Cleaned up temporary files")
    
    # Get the output filename
    base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
    
    if success:
        # Rename output to match input filename
        if os.path.exists(f"{base_name}.txt"):
            os.rename(f"{base_name}.txt", f"{base_name}_transcript.txt")
        print("✅ Transcription saved!")
    else:
        print("❌ Transcription failed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = 'path_to_your_audio_file'
    
    main(audio_file, language='zh')
