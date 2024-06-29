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
        
        #memo
            #24/05の観察にて、検出可能な上限のサンプリングレートに差があったため、(lick 10hz, NP 2hz)それぞれ定義。
            #6/26時点ではみられず。この結果がconfirmationされれば将来的には不要か。
            #6/27では5hz以上の検出で誤検出あり, 時たま検出遅れる？

        # 検出周波数の設定（lickとNPのためのサンプルレート）
        """
        行動の時定数(と思しきもの)よりも細かい周期とする
        将来的には統一する。
        24/06/28時点ではいずれも20hzでの検出は可能だが、
        NP検出のコード処理には,0.031秒かかっており、仮に気温湿度等による変動があれば(おそらくない)、バグが発生することも考えられ、そのような場合に備えて残しておく。
        """
        self.lick_detect_hz = 20  # Lick検出のためのサンプリングレート（Hz）
        self.NP_detect_hz = 20  # Nose poke検出のためのサンプリングレート（Hz）
        self.reward_offering_duration = 1  # 報酬提供の持続時間（秒）
        self.reward_stop_call_count = -1  # 報酬停止のためのカウンター

        # サンプリングレート比の計算
        sampling_ratio_ratio = self.lick_detect_hz / self.NP_detect_hz
        if not sampling_ratio_ratio.is_integer():
            raise ValueError("Lick and NP detection frequency ratio is not an integer.")

        self.time_out_in_s_NP = 3  # Nose pokeのタイムアウト時間（秒）
        self.call_count_last_NP_correct_list = [-1000, -1000, -1000, -1000]  # last NP_correctの記録場所

        self.results = dict()  # 状態の結果を格納する辞書
        self.call_count = -1  # 呼び出しカウンタ
        

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
            
        self.call_count = -1  # trialごとに初期化する。(必然性はないが軽量化のため)
        
        # Nose poke hole LEDを点灯
        correct_target_index_list = self._settings.get_correct_target_index_list()
        self._task_gpio.switch_nose_poke_leds('ON', correct_target_index_list)

        self._logger.info("NPmonitor start")
        start_time = time.perf_counter()　#ここから60秒間
        
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

        #  phase_settings.stimulus_duration_in_s(60秒間)経つと終了する。
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
            
            #この処理がここで良いのかは要検討。0.1秒程度かかる可能性があり、その場合他の検出を遅延させる可能性がある。
            # 最新のNP_correctから1秒経ったタイミングでrewardを停止する。
            if self.reward_stop_call_count == self.call_count:
                self._reward_offer.stop_offering()

        　　lick_is_pressed = self._task_gpio.check_lick(self.results)

            if lick_is_pressed:
                self._logger.info(self.name + ': Lick detected at ' + str(self.results['lick_time']))
                lick_time_list.append(self.results['lick_time'])

            #この条件分岐は、気温・湿度に対する検出の安定性が示されれば不要になる。
            if self.call_count % (self.lick_detect_hz/self.NP_detect_hz) == 0:
                reward_start_flag,self.call_count_last_NP_correct_list=self._check_nose_poke(nose_poke_time_list, nose_poke_hole_number_list,
                                      nose_poke_correct_time_list, nose_poke_hole_number_correct_list, self.call_count,self.call_count_last_NP_correct_list)
                
                if reward_start_flag != -1: 
                    
                    """
                    memo 24/06/28
                    reward_start_flagは、そのcallにおいて報酬供与開始条件が満たされた場合(NP_correct存在)、現在のcall_countを記録している。この場合、stop_call_countが、報酬停止予定call countとして更新される。-1だった場合は、NP_correctがなかったということなので、stop_call_countは更新しない。
                    この報酬提供開始操作には0.25秒程度かかり、これはhandlerのcall 間隔20hzよりも長いため、報酬提供開始とNPcorrect_listの書き換え作業は分離して行う必要がある。
                    0.25秒以内に他のreward開始指示が出された場合、バグが生じる可能性があるが、マウスが隣のNPholeに0.25秒以内に到達することはほぼ不可能と考えて良い。
                    """
                    
                    self._reward_offer.start_offering() # correct timeの登録より先に行うと、_give_rewardが重複して呼び出されるため(?, 要確認)注意
                    self.reward_stop_call_count = reward_start_flag + self.reward_offering_duration * self.lick_detect_hz
                    # 1000秒以内に異なるNP holeがNPされた場合、報酬提供の終了時間は更新される。
            
            

    def _check_nose_poke(self, nose_poke_time_list, nose_poke_hole_number_list, 
                         nose_poke_correct_time_list, nose_poke_hole_number_correct_list, call_count, call_count_last_NP_correct_list):
        # 初期値設定: 報酬開始のカウンターを-1にする（報酬を与えていないことを意味する）
        reward_start_flag = -1 
        nosepoke_selected_index=self._task_gpio.check_nose_poke_is_pressed(self.results)

        if nosepoke_selected_index is not None:
            # 選択されたNPhole名(番号)を取得
            reward_start_flag, call_count_last_NP_correct_list=self.process_and_record_NP(nosepoke_selected_index,nose_poke_time_list,nose_poke_hole_number_list,nose_poke_correct_time_list,nose_poke_hole_number_correct_list,call_count,call_count_last_NP_correct_list,reward_start_flag)
        
        return reward_start_flag, call_count_last_NP_correct_list


    def process_and_record_NP(self, nosepoke_selected_index,nose_poke_time_list, nose_poke_hole_number_list, 
                                   nose_poke_correct_time_list, nose_poke_hole_number_correct_list,call_count,call_count_last_NP_correct_list,reward_start_flag):
        #このhole_numに必要な_settingsには、gpio.pyからはアクセスできない。これがgpio.pyへの移行を妨げている。
        nose_poked_hole_num = self._settings.NOSE_POKE_TARGETS[nosepoke_selected_index]
        self.results['nose_poked_hole_num'] = nose_poked_hole_num
        nose_poke_time_list.append(self.results['nose_poke_time'])
        nose_poke_hole_number_list.append(self.results['nose_poked_hole_num'])
        self._logger.info(self.name + f'NP detected, NP{nose_poked_hole_num}')

        if call_count_last_NP_correct_list[nosepoke_selected_index] + self.time_out_in_s_NP*self.lick_detect_hz < call_count:
            nose_poke_correct_time_list.append(self.results['nose_poke_time'])
            nose_poke_hole_number_correct_list.append(self.results['nose_poked_hole_num'])
            self._logger.info(self.name + f'NP correct onset, NP correct onset {nose_poked_hole_num}') 
            reward_start_flag=call_count
            call_count_last_NP_correct_list[nosepoke_selected_index]=call_count
        return reward_start_flag, call_count_last_NP_correct_list #報酬供与があった場合は、その時の(call count,更新されたcall_count_last_NP_correct_list) なかった場合は(-1,同じcall_count_last_NP_correct_list)を返す。
    
