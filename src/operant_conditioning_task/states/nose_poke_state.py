#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" nose_poke_state.py
マウスの nose poke 状態を処理するクラスです。
"""

import time
import numpy as np
from transitions import State
import threading
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
        self._settings = kwargs['settings']# プログラム全体の設定です。
        self._task_gpio = kwargs['task_gpio']# GPIO のデジタル入出力を行うオブジェクトです。
        self._logger = kwargs['logger']# ログ出力を行うオブジェクトです。
        self._reward_offer=kwargs['reward_offer'] #rewardの提供を制御するオブジェクトです。
        
        #self.reward_offer=RewardOffer()

        #24/05の観察にて、検出可能な上限のサンプリングレートに差があったため、(lick 10hz, NP 2hz)それぞれ定義。
        # 6/26時点ではみられず。この結果がconfirmationされれば将来的には不要か。
        ##6/27では5hz以上の検出で誤検出あり, 時たま検出遅れる？
        self.lick_detect_hz=20
        self.NP_detect_hz=4
        self.reward_offering_duration=1 #second
        self.reward_stop_call_count=-1
        sampling_ratio_ratio = self.lick_detect_hz / self.NP_detect_hz
        # resultは整数値です
        if not sampling_ratio_ratio.is_integer():
            raise ValueError("lick NP detection hz ratio is not an integer.")

        self.time_out_in_s_NP = 3 #second
        self.call_count_last_NP_correct_list =[-1000,-1000,-1000,-1000]

        # 状態の結果データです。
        # 成功/失敗などの状態の結果は、self.results['state_result'] に StatusResult 列挙型で格納します。
        self.results = dict()
        self.call_count=-1

        

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

    def _monitor_nose_poke_task(self, phase_settings):
        if phase_settings.is_nose_poke_skip:
            self.results['state_result'] = TaskResult.Skipped
            self._logger.info(self.name + ': Skipped.')
            return
        
        # Nose poke hole LEDを点灯
        correct_target_index_list = self._settings.get_correct_target_index_list()
        self._task_gpio.switch_nose_poke_leds('ON', correct_target_index_list)

        self._logger.info("NPmonitor start")
        start_time = time.perf_counter()
        nose_poke_time_list, nose_poke_hole_number_list = [], []
        nose_poke_correct_time_list, nose_poke_hole_number_correct_list = [], []
        lick_time_list = []

        self.handler = functools.partial(self._combined_signal_handler, start_time=start_time, 
                                    phase_settings=phase_settings, 
                                    nose_poke_time_list=nose_poke_time_list, 
                                    nose_poke_hole_number_list=nose_poke_hole_number_list,
                                    nose_poke_correct_time_list=nose_poke_correct_time_list, 
                                    nose_poke_hole_number_correct_list=nose_poke_hole_number_correct_list,
                                    lick_time_list=lick_time_list)
        
        signal.signal(signal.SIGALRM, self.handler)
        signal.setitimer(signal.ITIMER_REAL, 1/self.lick_detect_hz, 1/self.lick_detect_hz)

        while signal.getitimer(signal.ITIMER_REAL)[0] != 0:
            time.sleep(0.05)  # CPU使用率を低下させるためにスリープ
        # LEDを消灯
        self._task_gpio.switch_nose_poke_leds('OFF')


    #周期的に呼び出されるhandler, lick検出の指定振動数で呼び出される。
    def _combined_signal_handler(self, signum, frame, start_time, phase_settings, 
                                 nose_poke_time_list, nose_poke_hole_number_list, 
                                 nose_poke_correct_time_list, nose_poke_hole_number_correct_list,
                                 lick_time_list):
        self.call_count+=1
        current_time = time.perf_counter()

        if current_time - start_time > phase_settings.stimulus_duration_in_s:
            signal.setitimer(signal.ITIMER_REAL, 0)
            self.results['state_result'] = TaskResult.Success
            self.results['nose_poke_time_list'] = nose_poke_time_list
            self.results['nose_poke_hole_number_list'] = nose_poke_hole_number_list
            self.results['nose_poke_correct_time_list'] = nose_poke_correct_time_list
            self.results['nose_poke_hole_number_correct_list'] = nose_poke_hole_number_correct_list
            self.results['lick_time_list'] = lick_time_list
            self._logger.info(f"{self.name}: Task monitoring finished.")

        else:
            # 最新のNP_correctから1秒経ったタイミングでrewardを停止する。
            if self.reward_stop_call_count == self.call_count:
                self._reward_offer.stop_offering()

            if self.call_count % (self.lick_detect_hz/self.NP_detect_hz) == 0:
                reward_start_flag,self.call_count_last_NP_correct_list=self._check_nose_poke(nose_poke_time_list, nose_poke_hole_number_list,
                                      nose_poke_correct_time_list, nose_poke_hole_number_correct_list, self.call_count,self.call_count_last_NP_correct_list)
                if reward_start_flag != -1: # 報酬供与開始を行なった場合は、報酬停止の時間を記録する。-1だった場合は、NP_correctがなかったということなので、stop_call_countは更新しない。
                    self.reward_stop_call_count = reward_start_flag + self.reward_offering_duration * self.lick_detect_hz
                    # 1000秒以内に異なるNP holeがNPされた場合、報酬提供の終了時間は更新される。
            lick_is_pressed = self._check_lick(lick_time_list)
            if lick_is_pressed:
                self._logger.info(self.name + ': Lick detected at ' + str(self.results['lick_time']))
                lick_time_list.append(self.results['lick_time'])

    def _check_nose_poke(self, nose_poke_time_list, nose_poke_hole_number_list, 
                         nose_poke_correct_time_list, nose_poke_hole_number_correct_list, call_count, call_count_last_NP_correct_list):
        # 初期値設定: 報酬開始のカウンターを-1にする（報酬を与えていないことを意味する）
        reward_start_flag = -1
        # handlerの呼び出しタイミングの間にnosepokeの開始(when_pressed信号)があったかををチェック
        if self._task_gpio.is_nose_poked: 
            self._task_gpio.get_nose_poke_results(self.results)
            nosepoke_selected_index=self.results['selected_index']
            reward_start_flag,self.call_count_last_NP_correct_list=self.process_and_record_NP(self,nosepoke_selected_index,nose_poke_time_list,nose_poke_hole_number_list,nose_poke_correct_time_list,nose_poke_hole_number_correct_list,call_count,call_count_last_NP_correct_list)
            self._task_gpio.reset_state(self.name)
            
        else:#NPセンサーに対する持続的な入力に対応するための実装
            #持続nose pokeへの対応：is_nose_pokeはfalseだが、信号入力がある場合
            nosepoke_selected_index=self._task_gpio.check_nose_poke_is_pressed(self.results)
            if nosepoke_selected_index is not None:
                # 選択されたNPhole名(番号)を取得
                reward_start_flag,self.call_count_last_NP_correct_list=self.process_and_record_NP(self,nosepoke_selected_index,nose_poke_time_list,nose_poke_hole_number_list,nose_poke_correct_time_list,nose_poke_hole_number_correct_list,call_count,call_count_last_NP_correct_list)
        return reward_start_flag, call_count_last_NP_correct_list
    

    def process_and_record_NP(self, nosepoke_selected_index,nose_poke_time_list, nose_poke_hole_number_list, 
                                   nose_poke_correct_time_list, nose_poke_hole_number_correct_list,call_count,call_count_last_NP_correct_list):
        nose_poked_hole_num = self._settings.NOSE_POKE_TARGETS[self.results['selected_index']]
        self.results['nose_poked_hole_num'] = nose_poked_hole_num
        nose_poke_time_list.append(self.results['nose_poke_time'])
        nose_poke_hole_number_list.append(self.results['nose_poked_hole_num'])
        self._logger.info(self.name + f'NP detected, NP{nose_poked_hole_num}')
        
        if call_count_last_NP_correct_list[nosepoke_selected_index] + self.time_out_in_s_NP*self.lick_detect_hz < call_count:
            nose_poke_correct_time_list.append(self.results['nose_poke_time'])
            nose_poke_hole_number_correct_list.append(self.results['nose_poked_hole_num'])
            self._logger.info(self.name + f'NP correct onset, NP correct onset {nose_poked_hole_num}') 
            self._reward_offer.start_offering() # correct timeの登録より先に行うと、_give_rewardが重複して呼び出されるため(?, 要確認)注意
            reward_start_flag=call_count
            call_count_last_NP_correct_list[nosepoke_selected_index]=call_count
            return reward_start_flag, call_count_last_NP_correct_list #報酬供与があった場合は、その時のcall count, なかった場合は-1を返す。
    
