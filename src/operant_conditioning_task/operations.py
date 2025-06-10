# 各フェーズに共通する操作を定義

import time
from hardware.task_gpio import TaskGpio, LedStatus
import hardware.speaker as speaker

class Operations:
    def __init__(self, gpio: TaskGpio):
        self._gpio = gpio

    # 報酬を与える. ブロッキング
    def give_reward(self) -> None:
        self._gpio.set_reward_led(LedStatus.ON)

        speaker.play_wav("hardware/6000Hz_sin_wave_96.wav")
        self._gpio.trigger_reward_pump()

        # すべての動作が1秒間続くように待機します。
        time.sleep(1)

        # 報酬用 LED を消灯します。
        self._gpio.set_reward_led(LedStatus.OFF)

        # WAVファイルの停止（もし音声ファイルの再生があれば）
        speaker.stop_wav()