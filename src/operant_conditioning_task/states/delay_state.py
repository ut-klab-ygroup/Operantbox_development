#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" delay_state.py
マウスの lick 課題成功後の待機状態を処理します。
"""

import time

from transitions import State

from states.task_result_enum import TaskResult


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

    # 状態開始時に呼び出される State クラスの on_enter コールバックです。
    # 待機状態の処理を開始します。
    def enter(self, event_data):
        self._logger.info(self.name + ': Started')

        # 状態の結果データを初期化します。
        self.results = dict()

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
    def _monitor_wait_task(self, phase_settings):

        # チャンバーの照明を消灯します。
        self._task_gpio.switch_chamber_light('OFF')

        # self.wait_time_in_s で指定した期間で待機します。
        start_time = time.perf_counter()
        while time.perf_counter() - start_time <= phase_settings.wait_time_in_s:

            # nose poke 行動が検出された場合、課題に失敗したとみなします。
            if self._task_gpio.is_nose_poked:
                self.results['state_result'] = TaskResult.Failure
                self._logger.info(self.name + ': Failure.')
                return

            time.sleep(0.001)

        self.results['state_result'] = TaskResult.Success
        self._logger.info(self.name + ': Success.')
