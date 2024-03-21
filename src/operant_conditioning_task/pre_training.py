import time
from gpiozero import LED, Button
import RPi.GPIO as GPIO
from settings.settings import Settings
import operant_conditioning_task as operant

def main():
    parser = operant.create_commandline_parser()
    args = parser.parse_args()

    # 設定ファイルを読み込み、設定オブジェクトを生成します。
    settings = Settings(args.experiment_name, args.setting_file_path)
    pin = LED(settings.pin_assignment['reward_pump'])

    # 無限ループで30秒おきに報酬を出す
    while True:
        pin.on()
        time.sleep(0.1)
        pin.off()

        time.sleep(30)

if __name__ == '__main__':
    main()