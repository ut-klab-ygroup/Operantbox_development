#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" task_gpio.py
# Raspberry Pi の GPIO によるデジタル入出力を行います。
"""

import time

from gpiozero import LED, LEDBoard, Button
import numpy as np


class TaskGpio:
    """
    Raspberry Pi の GPIO によるデジタル入出力を行います。
    """

    def __init__(self, pin_assignment, logger):

        # デジタル入出力を行うオブジェクトを生成します。
        self._chamber_light = LED(pin_assignment['chamber_light'])
        self._lick_sensor = Button(pin_assignment['lick_sensor'], hold_time=0.5, bounce_time=0.05)
        self._nose_poke_leds = LEDBoard(*pin_assignment['nose_poke_leds'])
        self._nose_poke_pin_assignment = np.array(pin_assignment['nose_poke_sensors'])
        self._nose_poke_sensors = []
        for i in range(len(pin_assignment['nose_poke_sensors'])):
           self._nose_poke_sensors.append(Button(pin_assignment['nose_poke_sensors'][i],
                                                 hold_time=0.5, bounce_time=0.05, active_state=True, pull_up=None))
        self._reward_led = LED(pin_assignment['reward_led'])
        self._reward_buzzer = LED(pin_assignment['reward_buzzer'])
        self._reward_pump = LED(pin_assignment['reward_pump'])

        # ログ出力を行うオブジェクトです。
        self._logger = logger


        # 現在の状態の名前です。
        self._state_name = ''
        
        # Lick 行動の結果です。
        self.is_licked = False
        self._lick_time = -1
        
        # Nose poke 行動の結果です。
        self.is_nose_poked = False
        self._nose_poke_time = -1
        self._nose_poke_selected_index = -1
        
        # Lick 行動と nose poke 行動の検出を開始します。
        self._detect_lick()
        self._detect_nose_poke()

    # 現在の状態を再設定します。
    def reset_state(self, state_name):
        self._state_name = state_name
        self.is_licked = False
        self._lick_time = -1
        self.is_nose_poked = False
        self._nose_poke_time = -1
        self._nose_poke_selected_index = -1

    # LED クラスを用いて、デバイスのスイッチング ('ON' と 'OFF') と点滅 ('Blink') を行います。
    def _switch_single_device(self, device, status, log=None):
        
        if log is not None:
            self._logger.debug(log)
            
        status = status.lower()
        if status == 'on':
            device.on()
        elif status == 'off':
            device.off()
        elif status == 'blink':
            device.blink(on_time=0.2, off_time=0.2, n=5, background=False)
        else:
            pass

    # LED クラスを用いて、デバイスにトリガーを掛けます。
    # トリガー パルスの幅は 100 msec です。
    def _trigger_single_device(self, device, log=None):

        if log is not None:
            self._logger.debug(log)

        device.on()
        time.sleep(0.1)
        device.off()

    # チャンバーの照明の点灯 ('ON')、消灯 ('OFF') あるいは点滅 ('Blink') を行います。
    def switch_chamber_light(self, status):
        log = self._state_name + ': Light ' + status.lower() + '.'
        self._switch_single_device(self._chamber_light, status, log)

    # Lick 行動の結果を results オブジェクトに格納します。
    def get_lick_results(self, results):
        results['lick_time'] = self._lick_time

    # Lick 行動を検出します。
    def _detect_lick(self):

        # Lick 行動用のセンサーが反応したときに呼び出されるコールバックです。
        def _lick_callback():
            if not self.is_licked:
                self.is_licked = True
                self._lick_time = time.time()
                self._logger.info(self._state_name + ': Licked.')
        self._lick_sensor.when_pressed = _lick_callback

    # target_index_list で指定したインデックスに対応する nose poke ターゲットの
    # LED の点灯 ('ON') あるいは消灯 ('OFF') を行います。
    # target_index_list で指定しない場合は、すべての LED を対象とします。
    def switch_nose_poke_leds(self, status, target_index_list = None):
        status = status.lower()
        if target_index_list is None:
            target_index_list = range(len(self._nose_poke_leds))
            
        if status == 'on':
            for target_index in target_index_list:
                self._nose_poke_leds[target_index].on()
            self._logger.debug(self._state_name + ': Nose poke LED on.')
        elif status == 'off':
            for target_index in target_index_list:
                self._nose_poke_leds[target_index].off()
            self._logger.debug(self._state_name + ': Nose poke LED off.')
        else:
            pass

    # Nose poke 行動の結果を results オブジェクトに格納します。
    def get_nose_poke_results(self, results):
        results['nose_poke_time'] = self._nose_poke_time
        results['selected_index'] = self._nose_poke_selected_index

    # Nose poke 行動を検出します。
    def _detect_nose_poke(self):

        # Nose poke 行動用のセンサーが反応したときに呼び出されるコールバックです。
        def _nose_poke_callback(sensor):
            if not self.is_nose_poked:
                self.is_nose_poked = True
                self._nose_poke_time = time.time()
                pin_name = str(sensor.pin)
                pin_num = int(pin_name.replace('GPIO', ''))
                selected_index = np.where(pin_num == self._nose_poke_pin_assignment)
                if selected_index[0].size > 0:
                    self._nose_poke_selected_index = selected_index[0][0]
                self._logger.info(self._state_name + ': Nose-poked.')

        # Nose poke の各ターゲットについて、コールバックを設定します。
        for sensor in self._nose_poke_sensors:
            sensor.when_pressed = _nose_poke_callback

    # 報酬用 LED の点灯 ('ON') あるいは消灯 ('OFF') を行います。
    def switch_reward_led(self, status):
        self._switch_single_device(self._reward_led, status)

    # 報酬用ブザーを鳴らします。
    def trigger_reward_buzzer(self):
        self._trigger_single_device(self._reward_buzzer)

    # 報酬用ポンプを駆動します。
    def trigger_reward_pump(self):
        self._trigger_single_device(self._reward_pump)

    def check_nose_poke_is_pressed(self,results):
        # 各センサーをチェックし、アクティブなセンサーのインデックスを取得
        for sensor in self._nose_poke_sensors:
            if sensor.is_pressed:
                results['nose_poke_time'] = time.time()
                pin_name = str(sensor.pin)
                pin_num = int(pin_name.replace('GPIO', ''))
                selected_index = np.where(pin_num == self._nose_poke_pin_assignment)
                if selected_index[0].size > 0:
                    results['selected_index'] = selected_index[0][0]
                    return selected_index[0][0]
        return None
    
    def check_lick(self, results):
        if self._lick_sensor.is_pressed:
            self._lick_time = time.time()
            self.get_lick_results(results)
            #self.reset_state(self.name)
            return True
        return False

    

# GPIO クラスのテスト
if __name__ == '__main__':
    
    print('===== GPIO test =====')
    
    from pathlib import Path
    import sys
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from utility import create_logger

    # GPIO ピンを設定します。
    pin_assignment = dict()
    pin_assignment['chamber_light'] = 20
    pin_assignment['lick_sensor'] = 16
    pin_assignment['nose_poke_leds'] = [26, 19, 13, 6, 5]
    pin_assignment['nose_poke_sensors'] = [24, 23, 18, 15, 14]
    pin_assignment['reward_led'] = 21
    pin_assignment['reward_buzzer'] = 2
    pin_assignment['reward_pump'] = 7

    # ログ出力を行うオブジェクトを生成します。
    logger = create_logger('./test_log.txt', True)

    # GPIO オブジェクトを生成します。
    taskGpio = TaskGpio(pin_assignment, logger)

    # 現在の状態を再設定します。
    taskGpio.reset_state('test')

    # チャンバーの照明をテストします。
    if True:
        taskGpio.switch_chamber_light('ON')
        time.sleep(1)
        taskGpio.switch_chamber_light('OFF')
        time.sleep(1)
        taskGpio.switch_chamber_light('Blink')

    # Lick 行動の検出をテストします。
    if False:
        taskGpio._detect_lick()
        while True:
            if taskGpio.is_licked:
                results = dict()
                taskGpio.get_lick_results(results)
                print(results['lick_time'])
                break
            time.sleep(1)

    # Nose poke ターゲットの LED をテストします。
    if False:
        taskGpio.switch_nose_poke_leds('ON')
        time.sleep(1)
        taskGpio.switch_nose_poke_leds('OFF')

    # Nose poke 行動の検出をテストします。
    if False:
        taskGpio._detect_nose_poke()
        while True:
            print(taskGpio.is_nose_poked)
            if taskGpio.is_nose_poked:
                results = dict()
                taskGpio.get_nose_poke_results(results)
                print(results['nose_poke_time'], results['selected_index'])
                break
            time.sleep(1)

    # 報酬用 LED をテストします。
    if False:
        taskGpio.switch_reward_led('ON')
        time.sleep(1)
        taskGpio.switch_reward_led('OFF')
        time.sleep(1)
        taskGpio.switch_reward_led('Blink')

    # 報酬用ブザーをテストします。
    if False:
        taskGpio.trigger_reward_buzzer()

    # 報酬用ポンプをテストします。
    if False:
        taskGpio.trigger_reward_pump()
    
    print('GPIO test: Passed.')
