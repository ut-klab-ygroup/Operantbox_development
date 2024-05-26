#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" nose_poke_state.py
マウスの nose poke 状態を処理するクラスです。
"""

import time

from transitions import State

from states.task_result_enum import TaskResult
from music import speaker

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

    # マウスの nose poke 課題を監視します。
    def _monitor_nose_poke_task(self, phase_settings):

        # Nose poke 課題をスキップする場合は何もしません。
        if phase_settings.is_nose_poke_skip:
            self.results['state_result'] = TaskResult.Skipped
            self._logger.info(self.name + ': Skipped.')
            return
        
        if self._settings.current_trial_num == 2:
            lick_time_list = []
            nose_poke_time_list = []
            nose_poke_hole_number_list = []
            nose_poke_correct_time_list = []
            nose_poke_hole_number_correct_list = []
            while time.perf_counter() - start_time <= phase_settings.stimulus_duration_in_s:
                if self._task_gpio.is_nose_poked:
                    self._task_gpio.get_nose_poke_results(self.results)
                    target_num = self._settings.NOSE_POKE_TARGETS[self.results['selected_index']]

                    self._task_gpio.reset_state(self.name)
                    #この遅延時間については要検討, 一括操作可能になると良いか。
                    time.sleep(0.05)
                    
                    self.results['target_num'] = target_num

                    nose_poke_time_list.append(self.results['nose_poke_time'])
                    nose_poke_hole_number_list.append(self.results['target_num'])
                    self._logger.info(self.name + f'NP detected, NP{target_num}')
                    
                    """
                    if self.results['selected_index'] in correct_target_index_list:
                        self.results['is_correct'] = True
                        self.results['state_result'] = TaskResult.Success
                        self._logger.info(self.name + f': Correct nose poke ({target_num}). Success.')
                    else:
                        self.results['is_correct'] = False
                        self.results['state_result'] = TaskResult.Failure
                        self._logger.info(self.name + f': Incorrect nose poke ({target_num}). Failure.')
                    """
                    ##nose_poke_time_listに格納されているunix timeについて、今回のnose pokeの時間がnose_poke_correct_time_listの最新のものから5秒以上経っていたら、という条件分岐。もしくは、nose_poke_correct_time_listが空だったら。##
                    if not nose_poke_correct_time_list or (self.results['nose_poke_time'] - nose_poke_correct_time_list[-1]) >= 5:
                        nose_poke_correct_time_list.append(self.results['nose_poke_time'])
                        nose_poke_hole_number_correct_list.append(self.results['target_num'])
                        self._logger.info(self.name + f'NP correct onset, NP correct onset {target_num}')
                    
                        self._give_reward() 
                    
                time.sleep(0.001)

                #nosepokeとlickの間には常に、一定間隔があく(>0.5s?)ため別処理で問題ない
                if self._task_gpio.is_licked:
                    #この処理によって、resultsの中にlick_timeが格納される。
                    self._task_gpio.get_lick_results(self.results)
                    lick_time_list.append(self.results['lick_time'])
                    self._logger.info(self.name + 'Lick detected')
                    time.sleep(0.01)
                    self._task_gpio.reset_state(self.name)
                    #この遅延時間については要検討, 一括操作可能になると良いか。
                    time.sleep(0.01)
                    
                    #self.results['state_result'] = TaskResult.Success
                    
                time.sleep(0.001)
            
            self.results['state_result'] = TaskResult.Success
            self.results['lick_time_list'] = lick_time_list
            self.results['nose_poke_time_list'] = nose_poke_time_list
            self.results['nose_poke_hole_number_list'] = nose_poke_hole_number_list
            self.results['nose_poke_correct_time_list'] = nose_poke_correct_time_list
            self.results['nose_poke_hole_number_correct_list'] = nose_poke_hole_number_correct_list
            
        else:
            # 正解の nose poke ターゲットの LED を点灯します。
            correct_target_index_list = self._settings.get_correct_target_index_list()
            self._task_gpio.switch_nose_poke_leds('ON', correct_target_index_list)

            # LED 刺激呈示期間において、nose poke 課題を監視します。
            # stimulus_duration_in_s = -1 の場合は、時間無制限です。
            start_time = time.perf_counter()
            while phase_settings.stimulus_duration_in_s == -1 or \
                    time.perf_counter() - start_time <= phase_settings.stimulus_duration_in_s:
                if self._task_gpio.is_nose_poked:
                    self._task_gpio.get_nose_poke_results(self.results)
                    target_num = self._settings.NOSE_POKE_TARGETS[self.results['selected_index']]
                    self.results['target_num'] = target_num
                    if self.results['selected_index'] in correct_target_index_list:
                        self.results['is_correct'] = True
                        self.results['state_result'] = TaskResult.Success
                        self._logger.info(self.name + f': Correct nose poke ({target_num}). Success.')
                    else:
                        self.results['is_correct'] = False
                        self.results['state_result'] = TaskResult.Failure
                        self._logger.info(self.name + f': Incorrect nose poke ({target_num}). Failure.')

                    # Nose poke ターゲットの LED を消灯します。
                    self._task_gpio.switch_nose_poke_leds('OFF')
                    return

                time.sleep(0.001)

            # Nose poke ターゲットの LED を消灯します。
            self._task_gpio.switch_nose_poke_leds('OFF')

            # limited_hold_in_s で指定された期間において、nose poke 課題を監視します。
            # stimulus_duration_in_s = -1 の場合は、時間無制限です。
            start_time = time.perf_counter()
            while phase_settings.stimulus_duration_in_s == -1 or \
                    time.perf_counter() - start_time < phase_settings.limited_hold_in_s:
                if self._task_gpio.is_nose_poked:
                    self._task_gpio.get_nose_poke_results(self.results)
                    target_num = self._settings.NOSE_POKE_TARGETS[self.results['selected_index']]
                    self.results['target_num'] = target_num
                    if self.results['selected_index'] in correct_target_index_list:
                        self.results['is_correct'] = True
                        self.results['state_result'] = TaskResult.Success
                        self._logger.info(self.name + f': Correct nose poke ({target_num}). Success.')
                    else:
                        self.results['is_correct'] = False
                        self.results['state_result'] = TaskResult.Failure
                        self._logger.info(self.name + f': Incorrect nose poke ({target_num}). Failure.')
                    return

                time.sleep(0.001)

            self.results['state_result'] = TaskResult.Timeout
            self._logger.info(self.name + ': Timeout.')

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
        time.sleep(5)

        # 報酬用 LED を消灯します。
        self._task_gpio.switch_reward_led('OFF')

        #WAVファイルの停止
        speaker.stop_wav()
