#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" timeout_state.py
課題のタイムアウト状態を処理します。
"""

import time

from transitions import State


class TimeoutState(State):
    """
    課題のタイムアウト状態を処理します。
    transitions ライブラリの State クラスを継承します。
    on_enter コールバックで、タイムアウト状態の処理を開始します。
    """

    # 状態オブジェクトを生成します。
    def __init__(self, *args, **kwargs):

        # State クラスのコンストラクターを呼び出します。
        super(TimeoutState, self).__init__(kwargs['name'])

        # ===== インスタンス変数 =====

        # プログラム全体の設定です。
        self.settings = kwargs['settings']

        # GPIO のデジタル入出力を行うオブジェクトです。
        self.task_gpio = kwargs['task_gpio']

        # ログ出力を行うオブジェクトです。
        self.logger = kwargs['logger']

    # 状態開始時に呼び出される State クラスの on_enter コールバックです。
    # タイムアウト状態の処理を開始します。
    def enter(self, event_data):
        self.logger.info(self.name + ': Started.')

        if self.settings.debug['skip_state']:
            time.sleep(2)
            self.logger.info(self.name + ': Finished.')
            return

        # フェーズ設定を取得します。
        phase_settings = self.settings.get_phase_settings()

        # GPIO の現在の状態を再設定します。
        self.task_gpio.reset_state(self.name)

        # タイムアウト状態の処理を行います。
        self._process_timeout(phase_settings)

        self.logger.debug(self.name + ': Finished.')

    # 状態終了時に呼び出される State クラスの on_exit コールバックです。
    def exit(self, event_data):
        pass

    # タイムアウト状態の処理を行います。
    def _process_timeout(self, phase_settings):

        # チャンバーの照明を点灯します。
        self.task_gpio.switch_chamber_light('ON')

        # self.timeout_in_s で指定した期間で待機します。
        start_time = time.perf_counter()
        while time.perf_counter() - start_time <= phase_settings.timeout_in_s:
            time.sleep(0.001)

        # チャンバーの照明を点滅します。
        self.task_gpio.switch_chamber_light('Blink')
