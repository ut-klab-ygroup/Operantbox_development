import time
import logging
from hardware.task_gpio import TaskGpio, LedStatus
from operations import Operations
from phases.phase import Phase
from sampler import Sampler

ON = LedStatus.ON
OFF = LedStatus.OFF

# settings
N_TRIALS = 60
TRIAL_TIMEOUT = 60
INTERVALS = [2, 3, 3, 5, 1, 4, 5, 4, 1, 2, 5, 4, 1, 5, 5, 3, 4, 2, 2, 4, 1, 2, 1, 5, 4, 1, 3, 2, 3, 1, 2, 5, 1, 4, 1, 3, 2, 3, 5, 1, 4, 5, 1, 5, 3, 5, 3, 2, 3, 4, 4, 1, 2, 2, 1, 1, 3, 5, 1, 1, 0]
NP_LEDS = [OFF, ON, ON, ON, OFF]

class Phase2(Phase):
    def __init__(self, gpio: TaskGpio, logger: logging.Logger, sampler: Sampler):
        self._gpio = gpio
        self._operations = Operations(gpio)
        self._logger = logger
        self._sampler = sampler
        self._trial = 0

    def get_trial(self) -> int:
        return self._trial
    
    def run(self):
        self.init()
        for i in range(N_TRIALS):
            self.run_trial()
            self.run_interval()
    
    def init(self):
        self._gpio.set_house_led(ON)
        self._gpio.set_nose_poke_leds(NP_LEDS)

    def run_trial(self):
        self._trial += 1
        self._sampler.set_trial_number(self._trial)
        self._logger.info(f"Trial{self._trial} started.")
        start_time = time.time()
        
        while time.time() - start_time < TRIAL_TIMEOUT:
            flag = self._gpio.get_and_clear_nose_poke_flag()
            if flag is not None:
                self._operations.give_reward()
                self._logger.debug(f"Nose poke detected ({flag})")
        
    def run_interval(self):
        duration = INTERVALS[self._trial % len(INTERVALS)]
        start_time = time.time()
        
        while time.time() - start_time < duration:
            flag = self._gpio.get_and_clear_nose_poke_flag()
            if flag is not None:
                self._operations.give_reward()
                self._logger.debug(f"Nose poke detected ({flag})")
