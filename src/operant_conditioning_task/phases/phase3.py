import time
import logging
from enum import Enum, auto

from hardware.task_gpio import TaskGpio, LedStatus
from operations import Operations
from phases.phase import Phase
from sampler import Sampler

ON = LedStatus.ON
OFF = LedStatus.OFF

# settings
N_TRIALS = 100
TRIAL_TIMEOUT = 60
EXPERIMENT_TIMEOUT = 60 * 60
INTERVALS = [2, 3, 3, 5, 1, 4, 5, 4, 1, 2, 5, 4, 1, 5, 5, 3, 4, 2, 2, 4, 1, 2, 1, 5, 4, 1, 3, 2, 3, 1, 2, 5, 1, 4, 1, 3, 2, 3, 5, 1, 4, 5, 1, 5, 3, 5, 3, 2, 3, 4, 4, 1, 2, 2, 1, 1, 3, 5, 1, 1, 0]
NP_LEDS_ON = [OFF, ON, ON, ON, OFF]
NP_LEDS_OFF = [OFF, OFF, OFF, OFF, OFF]

class TrialResult(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    EXP_TIMEOUT = auto()

class Phase3(Phase):
    def __init__(self, gpio: TaskGpio, logger: logging.Logger, sampler: Sampler):
        self._gpio = gpio
        self._operations = Operations(gpio)
        self._logger = logger
        self._sampler = sampler
        self._trial = 0
        self._experiment_deadline = -1

    def get_trial(self) -> int:
        return self._trial
    
    def run(self):
        self.init()
        for i in range(N_TRIALS):
            if self.wait_lick():
                return
            match self.run_trial():
                case TrialResult.SUCCESS:
                    self.give_reward()
                case TrialResult.FAILURE:
                    pass
                case TrialResult.EXP_TIMEOUT:
                    return
            
    
    def init(self):
        self._experiment_deadline = time.time() + EXPERIMENT_TIMEOUT
        self._gpio.set_house_led(ON)
        self._gpio.set_nose_poke_leds(NP_LEDS_OFF)

    def run_trial(self) -> TrialResult:
        start_time = time.time()
        self._trial += 1
        self._sampler.set_trial_number(self._trial)
        self._logger.info(f"Trial{self._trial} started.")

        self._gpio.set_house_led(OFF)
        self._gpio.set_nose_poke_leds(NP_LEDS_ON)

        while True:
            t = time.time()

            if t > self._experiment_deadline:
                self._logger.info("Experiment timed out.")
                return TrialResult.EXP_TIMEOUT

            if t - start_time > TRIAL_TIMEOUT:
                self._logger.info("Trial timed out.")
                return TrialResult.FAILURE

            flag = self._gpio.get_and_clear_nose_poke_flag()
            if flag is not None:
                self._logger.debug(f"Nose poke detected ({flag})")
                self._logger.info("Trial succeeded.")
                return TrialResult.SUCCESS

    # Experiment timeout の場合Trueを返す
    def wait_lick(self) -> bool:
        self._gpio.set_house_led(ON)
        return self._operations.wait_lick(self._experiment_deadline)
    
    def give_reward(self) -> None:
        self._gpio.set_house_led(OFF)
        self._gpio.set_nose_poke_leds(NP_LEDS_OFF)
        self._operations.give_reward()