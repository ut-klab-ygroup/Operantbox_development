import time
from task_gpio import LedStatus, task_gpio
from reward import give_reward

# settings
wait_time_in_s = 14
wait_time_list = [8,7,5,2,10,2,6,7,4,5,1,3,1,10,2,3,4,2,6,10,9,6,9,3,1,5,3,9,5,2,2,8,9,1,9,7,3,8,1,8,8,10,5,8,6,3,4,6,4,9,7,2,7,5,4,1,10,5,1,9,7,1,4,4,7,6,10,7,1,2,9,3,10,10,6,8,6,2,4,3,2,3,8,6,10,8,1,6,4,5,9,4,7,3,5,7,9,10,8,5]

def run():
    length = len(wait_time_list)
    for t in range(100):
        task_gpio.set_house_led(LedStatus.ON)
        
        time.sleep(wait_time_list[t % length] + wait_time_in_s)
        give_reward()
