
import time
from transitions import State
from music import speaker    

class RewardOffer():
    def __init__(self, *args, **kwargs):
        
        # ===== インスタンス変数 =====
        # プログラム全体の設定です。
        self._settings = kwargs['settings']
        # GPIO のデジタル入出力を行うオブジェクトです。
        self._task_gpio = kwargs['task_gpio']
        # ログ出力を行うオブジェクトです。
        self._logger = kwargs['logger']
        

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