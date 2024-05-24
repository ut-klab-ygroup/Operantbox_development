import pygame
import time

def play_wav(file_path):
    pygame.mixer.init(frequency=96000)
    pygame.mixer.music.load(file_path)

    print(f"Playing {file_path}")
    pygame.mixer.music.play()

def stop_wav():
    pygame.mixer.music.stop()

if __name__ == "__main__":
    # WAVファイルのパスを指定
    wav_file_path = "6000Hz_sin_wave_96.wav"

    # WAVファイルを再生
    play_wav(wav_file_path)

    time.sleep(5)

    stop_wav()