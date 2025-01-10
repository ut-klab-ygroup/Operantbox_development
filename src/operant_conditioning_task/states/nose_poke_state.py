#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" nose_poke_state.py
マウスの nose poke 状態を処理するクラスです。
"""

import time

from transitions import State

from states.task_result_enum import TaskResult


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
