import time
import logging
from phases.phase import Phase
from hardware.task_gpio import TaskGpio, LedStatus
from operations import Operations
from sampler import Sampler

# settings
wait_time_in_s = 14
wait_time_list = [8,7,5,2,10,2,6,7,4,5,1,3,1,10,2,3,4,2,6,10,9,6,9,3,1,5,3,9,5,2,2,8,9,1,9,7,3,8,1,8,8,10,5,8,6,3,4,6,4,9,7,2,7,5,4,1,10,5,1,9,7,1,4,4,7,6,10,7,1,2,9,3,10,10,6,8,6,2,4,3,2,3,8,6,10,8,1,6,4,5,9,4,7,3,5,7,9,10,8,5]

class Phase1(Phase):
    def __init__(self, gpio: TaskGpio, logger: logging.Logger, sampler: Sampler):
        self._gpio = gpio
        self._operations = Operations(gpio)
        self._trial = 0
        self._logger = logger
        self._sampler = sampler

    def get_trial(self) -> int:
        return self._trial

    def run(self):
        length = len(wait_time_list)
        for t in range(100):
            self._trial = t
            self._sampler.set_trial_number(self._trial)
            self._logger.info(f"Trial{self._trial} started.")

            self._gpio.set_house_led(LedStatus.ON)

            time.sleep(wait_time_list[t % length] + wait_time_in_s)
            self._operations.give_reward()
