# 各フェーズに共通する操作を定義
# インスタンスは作らずにクラスメソッドとして使用する

import time
from hardware.task_gpio import TaskGpio, LedStatus
import hardware.speaker as speaker

class Operations:
    # 報酬を与える. ブロッキング
    @staticmethod
    def give_reward(task_gpio: TaskGpio):
        task_gpio.set_reward_led(LedStatus.ON)

        speaker.play_wav("hardware/6000Hz_sin_wave_96.wav")
        task_gpio.trigger_reward_pump()

        # すべての動作が1秒間続くように待機します。
        time.sleep(1)

        # 報酬用 LED を消灯します。
        task_gpio.set_reward_led(LedStatus.OFF)

        # WAVファイルの停止（もし音声ファイルの再生があれば）
        speaker.stop_wav()