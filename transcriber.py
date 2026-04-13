import os
import sys
import subprocess
from pydub import AudioSegment

def compress_audio_smart(file_path, output_path, target_size_mb=50):
    """
    Compress audio intelligently based on duration to meet target size.
    For transcription, speech quality is preserved at 24-32 kbps.
    Uses AAC codec which is optimal for speech compression.
    """
    print(f"🔄 Analyzing audio file...")
    
    try:
        audio = AudioSegment.from_file(file_path)
        original_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        duration_minutes = len(audio) / 60000
        
        print(f"📊 Original: {original_size_mb:.2f}MB, Duration: {duration_minutes:.1f} min")
        
        # Calculate required bitrate to achieve target size
        # bitrate (kbps) = (target_size_mb * 8000) / duration_seconds
        duration_seconds = len(audio) / 1000
        required_bitrate_kbps = int((target_size_mb * 8000) / duration_seconds)
        
        # Clamp to reasonable range (24-48 kbps for speech)
        bitrate = max(24, min(48, required_bitrate_kbps))
        
        print(f"⚙️  Calculated bitrate: {bitrate}kbps to reach ~{target_size_mb}MB")
        
        # Export to AAC/M4A format (better compression than MP3 for speech)
        audio.export(output_path, format='mp4', bitrate=f'{bitrate}k', codec='aac')
        
        compressed_size = os.path.getsize(output_path) / (1024 * 1024)
        reduction = ((original_size_mb - compressed_size) / original_size_mb) * 100
        
        print(f"✅ Compressed: {original_size_mb:.2f}MB → {compressed_size:.2f}MB ({reduction:.1f}% reduction)")
        print(f"   Bitrate: {bitrate}kbps | Format: AAC/M4A (optimal for speech)")
        
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
    # Always compress large files to ensure <3min processing
    if file_size_mb > 10:
        print("⚡ File is large, compressing for faster processing...")
        # Target 40-50MB to ensure <3min transcription on CPU
        compressed_file = compress_audio_smart(
            audio_file_path, 
            'temp_compressed.m4a',
            target_size_mb=50  # Adjust based on your CPU speed
        )
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
