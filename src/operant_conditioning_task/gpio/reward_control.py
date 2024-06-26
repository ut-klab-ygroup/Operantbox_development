
import time
from transitions import State
from music import speaker  
#from gpio.task_gpio import TaskGpio  

class RewardOffer:
    def __init__(self, settings, task_gpio, logger):
        # インスタンス変数の設定
        self._settings = settings
        self._task_gpio = task_gpio
        self._logger = logger

    def start_offering(self):
        # 報酬用 LED を点灯します。
        self._task_gpio.switch_reward_led('ON')
        # 報酬用ブザーを鳴らします。
        self._task_gpio.trigger_reward_buzzer()
        speaker.play_wav("/home/share/Operantbox_development/src/operant_conditioning_task/music/6000Hz_sin_wave.wav")
        # シリンジ ポンプを駆動します。
        self._task_gpio.trigger_reward_pump()

    def stop_offering(self):
        # 報酬用 LED を消灯します。
        self._task_gpio.switch_reward_led('OFF')
        #WAVファイルの停止
        speaker.stop_wav()
    
    def give_reward(self):
        # 報酬用 LED を点灯します。
        self._task_gpio.switch_reward_led('ON')

        # 報酬用ブザーを鳴らします。
        #self._task_gpio.trigger_reward_buzzer()

        speaker.play_wav("/home/share/Operantbox_development/src/operant_conditioning_task/music/6000Hz_sin_wave.wav")

        # シリンジ ポンプを駆動します。
        self._task_gpio.trigger_reward_pump()

        # すべての動作が1秒間続くように待機します。
        time.sleep(1)

        # 報酬用 LED を消灯します。
        self._task_gpio.switch_reward_led('OFF')

        # ブザーの停止（もし必要であればコードを追加）
        #self._task_gpio.stop_reward_buzzer()

        # WAVファイルの停止（もし音声ファイルの再生があれば）
        speaker.stop_wav()