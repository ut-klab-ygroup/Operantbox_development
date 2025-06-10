import time
from gpiozero import LED, Button
from enum import Enum, auto

# ピン配置 (GPIO番号)
pin_assignment = {
    'house_led': 20,
    'nose_poke_leds': [26, 19, 13, 6, 5],
    'reward_led': 21,
    'reward_pump': 7,
    'lick_sensor': 16,
    'nose_poke_sensors': [24, 23, 18, 15, 14],
    'house_led_control': 27, #NIDAQ用回路を無効化
}

# LEDの状態用Enum
class LedStatus(Enum):
    ON = auto()
    OFF = auto()
    BLINK = auto()

# 定数
NOSE_POKE_REFRACTORY_PERIOD = 3 # ノーズポークの不応期 (秒)
LICK_REFRACTORY_PERIOD = 3      # リックの不応期 (秒)

class TaskGpio:
    """
    Raspberry Pi の GPIO によるデジタル入出力を行う
    """

    def __init__(self):
        # 出力系
        self._house_led = LED(pin_assignment['house_led'])
        self._nose_poke_leds = [LED(p) for p in pin_assignment['nose_poke_leds']]
        self._reward_led = LED(pin_assignment['reward_led'])
        self._reward_pump = LED(pin_assignment['reward_pump'])
        
        self._house_led_control = LED(pin_assignment['house_led_control']) # 基板のエラッタ対応用
        self._house_led_control.on()
        
        # 入力系
        self._lick_sensor = Button(pin_assignment['lick_sensor'], hold_time=0.5, bounce_time=0.05, active_state=True, pull_up=None)
        self._lick_sensor.when_pressed = self._lick_handler
        self._nose_poke_sensors = [
            Button(p, hold_time=0.5, bounce_time=0.05, active_state=True, pull_up=None)
            for p in pin_assignment['nose_poke_sensors']
        ]
        for dev in self._nose_poke_sensors:
            dev.when_pressed = self._nose_poke_handler

        # その他
        self._last_lick_time = 0
        self._last_nose_poke_times = [0 for _ in range(5)]
        self._lick_flag = False
        self._nose_poke_flag = None

    # 内部処理共通化用
    def _set_led(self, device: LED, status: LedStatus) -> None:
        match status:
            case LedStatus.ON:
                device.on()
            case LedStatus.OFF:
                device.off()
            case LedStatus.BLINK:
                device.blink(on_time=0.2, off_time=0.2, n=5, background=False)  # background: Falseだと終わるまでブロック

    # リック検出時のイベントハンドラ
    def _lick_handler(self):
        global event_licked
        t = time.time()
        if t - self._last_lick_time > LICK_REFRACTORY_PERIOD:
            self._last_lick_time = t
            self._lick_flag = True

    # ノーズポーク検出時のイベントハンドラ
    def _nose_poke_handler(self, dev: Button):
        global events_nose_poked
        idx = pin_assignment['nose_poke_sensors'].index(dev.pin.number)
        t = time.time()
        if t - self._last_nose_poke_times[idx] > NOSE_POKE_REFRACTORY_PERIOD:
            self._last_nose_poke_times[idx] = t
            self._nose_poke_flag = idx

    def set_house_led(self, status: LedStatus) -> None:
        self._set_led(self._house_led, status)
    
    def set_nose_poke_leds(self, statuses: list[LedStatus]) -> None:
        assert(len(statuses) == len(self._nose_poke_leds))
        for i in range(len(statuses)):
            self._set_led(self._nose_poke_leds[i], statuses[i])
    
    def set_reward_led(self, status: LedStatus) -> None:
        self._set_led(self._reward_led, status)

    # パルスを1回送る
    def trigger_reward_pump(self) -> None:
        self._reward_pump.blink(on_time=0.1, off_time=0.1, n=1, background=True)    # 100msのパルス, ノンブロッキング

    # リックセンサーの現在の状態を0または1で返す.
    def get_lick_sensor(self) -> int:
        return self._lick_sensor.value
    
    def get_nose_poke_sensors(self) -> list[int]:
        return [p.value for p in self._nose_poke_sensors]
    
    # リックのイベントフラグを取得する. 関数を呼ぶとフラグはクリアされる.
    def get_and_clear_lick_flag(self) -> bool:
        flag = self._lick_flag
        self._lick_flag = False
        return flag
    
    def get_and_clear_nose_poke_flag(self) -> int | None:
        flag = self._nose_poke_flag
        self._nose_poke_flag = None
        return flag
