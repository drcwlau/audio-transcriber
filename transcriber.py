import os
import sys
import time
import pydub
import speech_recognition as sr

def transcribe_audio(file_path, language='zh-CN', retries=3):
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Check the file format and load it accordingly
    file_format = file_path.split('.')[-1].lower()
    audio = None

    if file_format in ['wav']:
        audio = sr.AudioFile(file_path)
    else:
        # Convert mp3 or m4a to wav using pydub
        audio = pydub.AudioSegment.from_file(file_path)
        temp_wav_path = "temp.wav"
        audio.export(temp_wav_path, format='wav')
        audio = sr.AudioFile(temp_wav_path)

    transcription = ""
    with audio as source:
        audio_data = recognizer.record(source)
        
        # Retry logic for failed requests
        for attempt in range(retries):
            try:
                transcription += recognizer.recognize_google(audio_data, language=language) + "\n"
                break
            except sr.UnknownValueError:
                if attempt == retries - 1:
                    transcription += "[Audio unintelligible]\n"
            except sr.RequestError as e:
                if attempt == retries - 1:
                    transcription += f"[Error: {e}]\n"
                else:
                    time.sleep(2)  # Wait before retrying

    if 'temp_wav_path' in locals():
        os.remove(temp_wav_path)

    return transcription

def process_large_file(file_path, language='zh-CN'):
    # For large files, split the audio into chunks (30 seconds per chunk for better accuracy)
    chunk_duration_ms = 30000  # 30 seconds - smaller chunks = better accuracy
    audio = pydub.AudioSegment.from_file(file_path)

    transcripts = []
    total_chunks = len(audio) // chunk_duration_ms + 1
    
    for i in range(0, len(audio), chunk_duration_ms):
        chunk_num = i // chunk_duration_ms
        print(f"Processing chunk {chunk_num + 1}/{total_chunks}...")
        
        chunk = audio[i:i + chunk_duration_ms]
        chunk_path = f"chunk_{chunk_num}.wav"
        chunk.export(chunk_path, format='wav')
        
        transcript = transcribe_audio(chunk_path, language=language)
        transcripts.append(transcript)
        
        os.remove(chunk_path)
        time.sleep(1)  # Small delay between chunks to avoid rate limiting

    return ''.join(transcripts)

def main(audio_file_path, language='zh-CN'):
    if not os.path.exists(audio_file_path):
        print("Error: Audio file does not exist.")
        return

    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")

    if file_size_mb > 5:  # Lowered threshold from 10MB to 5MB for better chunking
        print("Processing as large file (chunked)...")
        transcription = process_large_file(audio_file_path, language=language)
    else:
        print("Processing as a regular file...")
        transcription = transcribe_audio(audio_file_path, language=language)

    # Output to text file
    output_file_path = os*
