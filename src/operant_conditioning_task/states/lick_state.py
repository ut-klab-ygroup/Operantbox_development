#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" lick_state.py
マウスの lick 状態を処理します。
"""

import time

from transitions import State

from states.task_result_enum import TaskResult


class LickState(State):
    """
    マウスの lick 状態を処理します。
    transitions ライブラリの State クラスを継承します。
    on_enter コールバックで、マウスの lick 状態の処理を開始します。
    """

    # 状態オブジェクトを生成します。
    def __init__(self, *args, **kwargs):

        # State クラスのコンストラクターを呼び出します。
        super(LickState, self).__init__(kwargs['name'])

        # ===== インスタンス変数 =====

        # プログラム全体の設定です。
        self._settings = kwargs['settings']

        # GPIO のデジタル入出力を行うオブジェクトです。
        self._task_gpio = kwargs['task_gpio']

        # 情報のログ出力を行うオブジェクトです。
        self._logger = kwargs['logger']

        self._reward_offer=kwargs['reward_offer'] #rewardの提供を制御するオブジェクトです。

        # 状態の結果データです。
        # 成功/失敗などの状態の結果は、self.results['state_result'] に StatusResult 列挙型で格納します。
        self.results = dict()

    # 状態開始時に呼び出される State クラスの on_enter コールバックです。
    # マウスの lick 状態の処理を開始します。
    def enter(self, event_data):
        self._logger.info(self.name + ': Started.')

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

        # マウスの lick 課題を監視します。
        self._monitor_lick_task(phase_settings)

        self._logger.debug(self.name + ': Finished.')

    # 状態終了時に呼び出される State クラスの on_exit コールバックです。
    def exit(self, event_data):
        pass

    # マウスの lick 課題を監視します。
    def _monitor_lick_task(self, phase_settings):

        # lick 課題をスキップする場合は何もしません。
        if not phase_settings.is_lick_wait:
            self.results['state_result'] = TaskResult.Skipped
            self._logger.info(self.name + ': Skipped.')
            return

        # チャンバーの照明を点灯します。
        self._task_gpio.switch_chamber_light('ON')
        self.results['light_on_time'] = time.time()

        # lick 行動、あるいは nose poke 行動が検出されるまで監視を行います。
        while True:
            # lick 行動が検出された場合、課題に成功したとみなします。
            if self._task_gpio.is_licked:
                self._task_gpio.get_lick_results(self.results)
                self.results['state_result'] = TaskResult.Success
                self._logger.info(self.name + ': Success.')
                return
            # nose poke 行動が検出された場合、課題に失敗したとみなします。
            elif self._task_gpio.is_nose_poked and phase_settings.is_perservative:
                self._task_gpio.get_nose_poke_results(self.results)
                self.results['state_result'] = TaskResult.Failure
                self._logger.info(self.name + ': Failure.')
                return

            time.sleep(0.001)
