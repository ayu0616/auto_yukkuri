import subprocess
import glob


def convert_to_wav(voice_files):
    for voice_file in voice_files:
        subprocess.run(f"yes y | ffmpeg -i {voice_file} -vn -ac 1 -ar 44100 -acodec pcm_s16le -f wav {voice_file.replace('mp3', 'wav')}", shell=True, check=True)
    voice_files = list(map(lambda x: x.replace("mp3", "wav"), voice_files))
    return voice_files


if __name__ == "__main__":
    voice_files = glob.glob("../voices/mp3/*")
    voice_files.sort()
    convert_to_wav(voice_files)
