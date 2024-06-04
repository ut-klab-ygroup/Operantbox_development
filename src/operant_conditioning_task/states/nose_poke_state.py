#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" nose_poke_state.py
マウスの nose poke 状態を処理するクラスです。
"""

import time
import numpy as np
from transitions import State

from states.task_result_enum import TaskResult
from music import speaker
import signal
import functools

class NosePokeState(State):
    """
    マウスの nose poke 状態を処理します。
    transitions ライブラリの State クラスを継承します。
    on_enter コールバックで、マウスの nose poke 状態の処理を開始します。
    """

    # 状態オブジェクトを生成します。
    def __init__(self, *args, **kwargs):

        # State クラスのコンストラクターを呼び出します。
        super(NosePokeState, self).__init__(kwargs['name'])

        # ===== インスタンス変数 =====

        # プログラム全体の設定です。
        self._settings = kwargs['settings']

        # GPIO のデジタル入出力を行うオブジェクトです。
        self._task_gpio = kwargs['task_gpio']

        # ログ出力を行うオブジェクトです。
        self._logger = kwargs['logger']

        # 状態の結果データです。
        # 成功/失敗などの状態の結果は、self.results['state_result'] に StatusResult 列挙型で格納します。
        self.results = dict()

    # 状態開始時に呼び出される State クラスの on_enter コールバックです。
    # マウスの nose poke 状態の処理を開始します。
    def enter(self, event_data):
        self._logger.info(self.name + ': Started.')

        # 状態の結果データを初期化します。
        self.results = dict()

        if self._settings.debug['skip_state']:
            time.sleep(2)
            self.results['state_result'] = TaskResult.Success
            self._logger.info(self.name + ': Finished.')
            return

        # フェーズ設定を取得します。
        phase_settings = self._settings.get_phase_settings()

        # GPIO の現在の状態を再設定します。
        self._task_gpio.reset_state(self.name)

        # マウスの nose poke 課題を監視します。
        self._monitor_nose_poke_task(phase_settings)

        self._logger.debug(self.name + ': Finished.')
    
    # 状態終了時に呼び出される State クラスの on_exit コールバックです。
    def exit(self, event_data):
        pass
    

    def _signal_handler(self, signum, frame, start_time, phase_settings, nose_poke_time_list, nose_poke_hole_number_list, nose_poke_correct_time_list, nose_poke_hole_number_correct_list, lick_time_list,reward_time_list):
        # 時間の確認
        current_time = time.perf_counter()
        if current_time - start_time > phase_settings.stimulus_duration_in_s:
            # タイマーを停止
            signal.setitimer(signal.ITIMER_REAL, 0)
            # 成功として記録
            self.results['state_result'] = TaskResult.Success
            self.results['lick_time_list'] = lick_time_list
            self.results['nose_poke_time_list'] = nose_poke_time_list
            self.results['nose_poke_hole_number_list'] = nose_poke_hole_number_list
            self.results['nose_poke_correct_time_list'] = nose_poke_correct_time_list
            self.results['nose_poke_hole_number_correct_list'] = nose_poke_hole_number_correct_list
            self._logger.info(f"{self.name}: Task monitoring finished.")
            return
        else:
            
            if self._task_gpio.is_nose_poked: #これだとNPが終わらないと呼び出されない。またNP3が呼び出されない。
                self._nose_poke_callback_phase2(nose_poke_time_list,nose_poke_hole_number_list,nose_poke_correct_time_list,nose_poke_hole_number_correct_list)
                self._task_gpio.reset_state(self.name)

            if not self._task_gpio.is_nose_poked:
                for sensor in self._task_gpio._nose_poke_sensors:
                    if sensor.is_pressed:
                        self._task_gpio._nose_poke_time = time.time()
                        self.results['nose_poke_time'] = self._task_gpio._nose_poke_time
                        self.results['selected_index'] = self._task_gpio._nose_poke_selected_index
                        pin_name = str(sensor.pin)
                        pin_num = int(pin_name.replace('GPIO', ''))
                        selected_index = np.where(pin_num == self._task_gpio._nose_poke_pin_assignment)
                        if selected_index[0].size > 0:
                            #print(selected_index)
                            nosepoke_selected_index = selected_index[0][0]
                            target_num = self._settings.NOSE_POKE_TARGETS[nosepoke_selected_index]
                        self.results['target_num'] = target_num
                        #print(target_num)
                        nose_poke_time_list.append(self.results['nose_poke_time'])
                        nose_poke_hole_number_list.append(self.results['target_num'])
                        self._logger.info(self.name + f'NP detected, NP{target_num}')
                        if not nose_poke_correct_time_list or (self.results['nose_poke_time'] - nose_poke_correct_time_list[-1]) >= 3:
                            nose_poke_correct_time_list.append(self.results['nose_poke_time'])
                            nose_poke_hole_number_correct_list.append(self.results['target_num'])
                            self._logger.info(self.name + f'NP correct onset, NP correct onset {target_num}')
                            self._give_reward() # correct timeの登録より先に行うと、NPの間中loopをしてしまうため注意
                            time.sleep(0.001)
   
            # 舐め検出
            if self._task_gpio._lick_sensor.is_pressed:
                self._task_gpio._lick_time = time.time()
                self._task_gpio.get_lick_results(self.results)
                self._logger.info(self.name + ': Lick detected at ' + str(self.results['lick_time']))
                    ##lick_timeの検出は01で行っても良い。
                #lick_time_list.append(current_time - start_time)
                lick_time_list.append(self.results['lick_time'])
                self._task_gpio.reset_state(self.name) 

        # タイマーを再設定（0.1秒ごとにチェック）
        #signal.setitimer(signal.ITIMER_REAL, 0.5)

    def _monitor_nose_poke_task(self, phase_settings):

        if phase_settings.is_nose_poke_skip:
            self.results['state_result'] = TaskResult.Skipped
            self._logger.info(self.name + ': Skipped.')
            return
        #print("kokomade")
        #if self._settings.current_trial_num == 2:
        print("NPmonitor start")
    # LEDを点灯
        correct_target_index_list = self._settings.get_correct_target_index_list()
        self._task_gpio.switch_nose_poke_leds('ON', correct_target_index_list)

        # 監視開始時間の記録
        start_time = time.perf_counter()
        nose_poke_time_list = []
        nose_poke_hole_number_list = []
        nose_poke_correct_time_list = []
        nose_poke_hole_number_correct_list = []
        lick_time_list = []
        reward_time_list=[]

        while time.perf_counter() - start_time <= phase_settings.stimulus_duration_in_s:
                
            # シグナルハンドラーの設定
            handler = functools.partial(self._signal_handler, start_time=start_time, phase_settings=phase_settings, 
                                        nose_poke_time_list=nose_poke_time_list, nose_poke_hole_number_list=nose_poke_hole_number_list,
                                        nose_poke_correct_time_list=nose_poke_correct_time_list, nose_poke_hole_number_correct_list=nose_poke_hole_number_correct_list,
                                        lick_time_list=lick_time_list,reward_time_list=reward_time_list)
            signal.signal(signal.SIGALRM, handler)

            # タイマーを設定（0.1秒ごとにチェック）
            signal.setitimer(signal.ITIMER_REAL, 0.5, 0.5)

            # タイマーが停止するまで待機
            while signal.getitimer(signal.ITIMER_REAL)[0] != 0:
                time.sleep(0.1)  # CPU使用率を低下させるためにスリープ

            # LEDを消灯
            self._task_gpio.switch_nose_poke_leds('OFF')

    def _nose_poke_callback_phase2(self,nose_poke_time_list,nose_poke_hole_number_list,nose_poke_correct_time_list,nose_poke_hole_number_correct_list):
        #self._task_gpio._nose_poke_time = time.time()
        self._task_gpio.get_nose_poke_results(self.results)
        target_num = self._settings.NOSE_POKE_TARGETS[self.results['selected_index']]
        self.results['target_num'] = target_num
        #print(target_num)
        nose_poke_time_list.append(self.results['nose_poke_time'])
        nose_poke_hole_number_list.append(self.results['target_num'])
        self._logger.info(self.name + f'NP detected, NP{target_num}')
        if not nose_poke_correct_time_list or (self.results['nose_poke_time'] - nose_poke_correct_time_list[-1]) >= 3:
            nose_poke_correct_time_list.append(self.results['nose_poke_time'])
            nose_poke_hole_number_correct_list.append(self.results['target_num'])
            self._logger.info(self.name + f'NP correct onset, NP correct onset {target_num}')
            self._give_reward()
        
    # 報酬を付与します。
    def _give_reward(self):

        # 報酬用 LED を点灯します。
        self._task_gpio.switch_reward_led('ON')

        # 報酬用ブザーを鳴らします。
        self._task_gpio.trigger_reward_buzzer()

        speaker.play_wav("/home/share/Operantbox_development/src/operant_conditioning_task/music/6000Hz_sin_wave.wav")

        # シリンジ ポンプを駆動します。
        self._task_gpio.trigger_reward_pump()

        # 報酬用 LED の点灯時間を調整します。
        time.sleep(1)

        # 報酬用 LED を消灯します。
        self._task_gpio.switch_reward_led('OFF')

        #WAVファイルの停止
        speaker.stop_wav()
