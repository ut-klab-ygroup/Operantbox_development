from phases.phase1 import Phase1
from phases.phase2 import Phase2
import logger
from hardware.task_gpio import TaskGpio
from sampler import Sampler

def main():
    log = logger.create_logger("log_files/test.txt")
    gpio = TaskGpio()
    sampler = Sampler(gpio, "results_files/test.csv")

    phase = Phase2(gpio, log, sampler)

    try:
        phase.run()
    finally:
        sampler.cleanup()

if __name__ == '__main__':
    main()
