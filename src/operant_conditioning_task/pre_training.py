import time
from gpiozero import LED, Button
import RPi.GPIO as GPIO
from settings.settings import Settings
import operant_conditioning_task as operant

class Trigger:
    def __init__(self, pin):
        self._pin = LED(pin)

    def pulse(self):
        self._pin.on()
        time.sleep(0.1)
        self._pin.off()

def main():
    parser = operant.create_commandline_parser()
    args = parser.parse_args()

    # 設定ファイルを読み込み、設定オブジェクトを生成します。
    settings = Settings(args.experiment_name, args.setting_file_path)
    trigger = Trigger(settings.pin_assignment['reward_pump'])

    # 無限ループで30秒おきに30分間報酬を出す
    for i in range (60):
        print(f'{i+1}/60')
        trigger.pulse()
        time.sleep(30)
    
    print('finished')

if __name__ == '__main__':
    main()