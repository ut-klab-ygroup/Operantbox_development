import time
import music.speaker as speaker
from task_gpio import LedStatus, task_gpio

# 報酬を与える. ブロッキング
def give_reward():
    task_gpio.set_reward_led(LedStatus.ON)

    speaker.play_wav("music/6000Hz_sin_wave_96.wav")
    task_gpio.trigger_reward_pump()

    # すべての動作が1秒間続くように待機します。
    time.sleep(1)

    # 報酬用 LED を消灯します。
    task_gpio.set_reward_led(LedStatus.OFF)

    # WAVファイルの停止（もし音声ファイルの再生があれば）
    speaker.stop_wav()