#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" delay_state.py
マウスの lick 課題成功後の待機状態を処理します。
"""

import time
import signal

from transitions import State

from states.task_result_enum import TaskResult
from state_machine.task_results import TaskResults #作業ディレクトリ的にできるか？
import functools
import threading
from music import speaker

class DelayState(State):
    """
    マウスの lick 課題成功後の待機状態を処理します。
    transitions ライブラリの State クラスを継承します。
    on_enter コールバックで、待機状態の処理を開始します。
    """

    # 状態オブジェクトを生成します。
    def __init__(self, *args, **kwargs):
        # State クラスのコンストラクターを呼び出します。
        super(DelayState, self).__init__(kwargs['name'])
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
        self.lick_detect_hz=20
        self.call_counts_list=[]
        self.reward_given =False
        self.reward_offering_time = 5
        self.call_count=-1
        self.handler = functools.partial(self._signal_handler, wait_time=wait_time, lick_time_list=lick_time_list, start_time=start_time)

    # 状態開始時に呼び出される State クラスの on_enter コールバックです。
    # 待機状態の処理を開始します。
    def enter(self, event_data):
        self._logger.info(self.name + ': Started')
        # 状態の結果データを初期化します。
        self.results = dict()
        #以下はdebugする時用
        if self._settings.debug['skip_state']:
            time.sleep(2)
            self.results['state_result'] = TaskResult.Success
            self._logger.info(self.name + ': Finished')
            return

        # フェーズ設定を取得します。
        phase_settings = self._settings.get_phase_settings()
        # GPIO の現在の状態を再設定します。
        self._task_gpio.reset_state(self.name)
        # 待機課題を監視します。
        self._monitor_wait_task(phase_settings)
        self._logger.debug(self.name + ': Finished')
        

    # 状態終了時に呼び出される State クラスの on_exit コールバックです。
    def exit(self, event_data):
        pass

    # 待機課題を監視します。
    

    def _signal_handler(self, signum, frame, wait_time, lick_time_list, start_time):
        self.call_count+=1
        
        # delay state開始から一定時間後にreward 提供 #現状の実装では5秒後
        if call_count == self.lick_detect_hz* self.reward_offering_time:
            reward_time = time.time()
            self._give_reward()
            self._logger.info("Giving Reward at " + str(reward_time))
            
        if time.perf_counter() - start_time > wait_time:#phase_settings.wait_time_in_s:
            # Stop the alarm timer.
            signal.setitimer(signal.ITIMER_REAL, 0)
            # Record the success and log it.
            self.results['state_result'] = TaskResult.Success
            self.results['lick_time_list'] = lick_time_list
            self._logger.info(f"{self.name}: Success")# with lick times: {lick_time_list}")
            self.reward_given =False
            
        else:
            
            if self._task_gpio._lick_sensor.is_pressed:
                self._task_gpio._lick_time = time.time()
                self._task_gpio.get_lick_results(self.results)
                self._logger.info(self.name + ': Lick detected at ' + str(self.results['lick_time']))
                lick_time_list.append(self.results['lick_time'])
                self._task_gpio.reset_state(self.name) 
                    #reset_stateをここで行わないとlick_timeが更新されない。
                    #todo：調査@240602
                        ##→そもそもtask.gpioのresultsを使わなければチャタリングの問題も生じなさそうで20hzでの検出も可能か？それかsignalハンドラーによる呼び出しそのものでチャタリング的なこと起こる？？
                #self._logger.info(f"{self.name}: Lick detected at {current_time - start_time} seconds")
                    #time.sleep(1)
            

    def _monitor_wait_task(self, phase_settings):

        if phase_settings.wait_time_in_s == 0:
        #phase_settings.delay_state_skip:
            #print("skip")
            self.results['state_result'] = TaskResult.Skipped
            self._logger.info(self.name + ': Skipped.')
            return

        # Turn off the chamber light.
        self._task_gpio.switch_chamber_light('OFF')
        start_time = time.perf_counter()
        wait_list = phase_settings.wait_time_list
        wait_time = phase_settings.wait_time_in_s + wait_list[(self._settings.current_trial_num - 1) % len(wait_list)]
        lick_time_list = []

        # Set the signal handler for SIGALRM.
        signal.signal(signal.SIGALRM, self.handler)
        # Configure the timer to fire every 0.1 seconds.
        signal.setitimer(signal.ITIMER_REAL, 1/self.lick_detect_hz, 1/self.lick_detect_hz)

        # Wait for the signal handler to end the monitoring.
        while signal.getitimer(signal.ITIMER_REAL)[0] != 0:
            time.sleep(0.1)  # Sleep to prevent high CPU usage, only wake to check if timer is still running.

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
