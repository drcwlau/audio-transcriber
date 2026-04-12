import os
import sys
import pydub
import speech_recognition as sr

def transcribe_audio(file_path):
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
        try:
            transcription += recognizer.recognize_google(audio_data) + "\n"
        except sr.UnknownValueError:
            transcription += "Audio unintelligible\n"
        except sr.RequestError as e:
            transcription += f"Could not request results from Google Speech Recognition service; {e}\n"

    if 'temp_wav_path' in locals():
        os.remove(temp_wav_path)

    return transcription

def process_large_file(file_path):
    # For large files, split the audio into chunks (example: 60 seconds)
    chunk_duration_ms = 60000  # 1 minute
    audio = pydub.AudioSegment.from_file(file_path)

    transcripts = []
    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        chunk_path = f"chunk_{i // chunk_duration_ms}.wav"
        chunk.export(chunk_path, format='wav')
        transcript = transcribe_audio(chunk_path)
        transcripts.append(transcript)
        os.remove(chunk_path)

    return ''.join(transcripts)

def main(audio_file_path):
    if not os.path.exists(audio_file_path):
        print("Error: Audio file does not exist.")
        return

    if os.path.getsize(audio_file_path) > 10 * 1024 * 1024:
        print("Processing as large file...")
        transcription = process_large_file(audio_file_path)
    else:
        print("Processing as a regular file...")
        transcription = transcribe_audio(audio_file_path)

    # Output to text file
    output_file_path = os.path.splitext(audio_file_path)[0] + "_transcript.txt"
    with open(output_file_path, 'w') as f:
        f.write(transcription)
    print(f"Transcription saved to {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = 'path_to_your_audio_file'
    
    main(audio_file)
