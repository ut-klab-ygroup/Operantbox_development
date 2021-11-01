#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" reward_state.py
報酬状態を処理します。
"""

import time

from transitions import State


class RewardState(State):
    """
    報酬状態を処理します。
    transitions ライブラリの State クラスを継承します。
    on_enter コールバックで、報酬状態を処理を開始します。
    """

    # 状態オブジェクトを生成します。
    def __init__(self, *args, **kwargs):

        # State クラスのコンストラクターを呼び出します。
        super(RewardState, self).__init__(kwargs['name'])

        # ===== インスタンス変数 =====

        # プログラム全体の設定です。
        self.settings = kwargs['settings']

        # GPIO のデジタル入出力を行うオブジェクトです。
        self.task_gpio = kwargs['task_gpio']

        # ログ出力を行うオブジェクトです。
        self.logger = kwargs['logger']

    # 状態開始時に呼び出される State クラスの on_enter コールバックです。
    # 報酬状態を処理を開始します。
    def enter(self, event_data):
        self.logger.info(self.name + ': Started.')

        if self.settings.debug['skip_state']:
            time.sleep(2)
            self.logger.info(self.name + ': Finished.')
            return

        # GPIO の現在の状態を再設定します。
        self.task_gpio.reset_state(self.name)

        # 報酬を付与します。
        self._give_reward()

        self.logger.debug(self.name + ': Finished.')

    # 状態終了時に呼び出される State クラスの on_exit コールバックです。
    def exit(self, event_data):
        pass

    # 報酬を付与します。
    def _give_reward(self):

        # 報酬用 LED を点灯します。
        self.task_gpio.switch_reward_led('ON')

        # 報酬用ブザーを鳴らします。
        self.task_gpio.trigger_reward_buzzer()

        # シリンジ ポンプを駆動します。
        self.task_gpio.trigger_reward_pump()

        # 報酬用 LED の点灯時間を調整します。
        time.sleep(5)

        # 報酬用 LED を消灯します。
        self.task_gpio.switch_reward_led('OFF')
