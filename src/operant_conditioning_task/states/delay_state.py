#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" delay_state.py
マウスの lick 課題成功後の待機状態を処理します。
"""

import time

from transitions import State

from states.task_result_enum import TaskResult
from state_machine.task_results import TaskResults #作業ディレクトリ的にできるか？


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
    def _monitor_wait_task(self, phase_settings):

        # チャンバーの照明を消灯します。
        self._task_gpio.switch_chamber_light('OFF')

        # self.wait_time_in_s で指定した期間で待機します。
        start_time = time.perf_counter()
        wait_list = phase_settings.wait_time_list
        wait_time = phase_settings.wait_time_in_s + wait_list[(self._settings.current_trial_num - 1) % len(wait_list)]
        lick_time_list = []
        while time.perf_counter() - start_time <= wait_time:
            """
            #現状の実装では不要、一旦外す、。
            #将来的には、現在のphaseを指定するor is_persevativeをつけるだけでいいか？
            # nose poke 行動が検出された場合、課題に失敗したとみなします。
            if self._task_gpio.is_nose_poked:# and phase_settings.is_perservative:
                self.results['state_result'] = TaskResult.Failure
                self._logger.info(self.name + ': Failure.')
                return
            """
            if self._task_gpio.is_licked:
                #この処理によって、resultsの中にlick_timeが格納される。
                self._task_gpio.get_lick_results(self.results)
                lick_time_list.append(self.results['lick_time'])
                #self.results['state_result'] = TaskResult.Success
                self._logger.info(self.name + 'Lick detected')
            """
            2024/5/24 大石
            _task_gpio.is_licled はリックセンサーに反応があった時にTrueになるのですが、Falseにするのは読み出し側が行う必要があります。
            例えば lick_state.py では enter() の中で _task_gpio.reset_state() を呼び出して is_licked を False にしてから
            _monitor_lick_task() を行い, is_licked が True になるのを監視しています。
            このコードでは is_licked を False にしていないので毎ループで記録されてしまう可能性があります。
            is_licked が True になるたびに False にすればいいかというとセンサーのチャタリングなどの問題があるので単純にはいかなくて要検討です。
            """
                
            time.sleep(0.001)

        self.results['state_result'] = TaskResult.Success
        self.results['lick_time_list'] = lick_time_list
        self._logger.info(self.name + ': Success.')
