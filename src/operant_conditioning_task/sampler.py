import signal, time
from hardware.task_gpio import TaskGpio

class Sampler:
    def __init__(self, gpio: TaskGpio, result_file: str):
        self._gpio = gpio
        self._file = open(result_file, "w")
        self._result_file = result_file
        self._trial = 0

        # 20Hzのタイマーとシグナルハンドラの登録
        signal.setitimer(signal.ITIMER_REAL, 0.05, 0.05)
        signal.signal(signal.SIGALRM, self._signal_handler)

        self._file.write("time,trial,lick,np0,np1,np2,np3,np4\n")
    
    # センサーの値をファイルに書き込み
    def _signal_handler(self, signum, frame):
        if self._file.closed:
            return
        t = time.time()
        lick = self._gpio.get_lick_sensor()
        nose_pokes = self._gpio.get_nose_poke_sensors()
        values = [t, self._trial, lick] + nose_pokes
        s = ",".join(str(n) for n in values) + "\n"
        self._file.write(s)

    def set_trial_number(self, trial: int) -> None:
        self._trial = trial

    def cleanup(self) -> None:
        self._file.close()