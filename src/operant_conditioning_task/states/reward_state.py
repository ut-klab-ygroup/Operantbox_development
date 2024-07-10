#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" reward_state.py
報酬状態を処理します。
"""

import time

from transitions import State

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from music import speaker

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
        self._settings = kwargs['settings']

        # GPIO のデジタル入出力を行うオブジェクトです。
        self._task_gpio = kwargs['task_gpio']

        # ログ出力を行うオブジェクトです。
        self._logger = kwargs['logger']

    # 状態開始時に呼び出される State クラスの on_enter コールバックです。
    # 報酬状態を処理を開始します。
    def enter(self, event_data):
        self._logger.info(self.name + ': Started.')

        if self._settings.debug['skip_state']:
            time.sleep(2)
            self._logger.info(self.name + ': Finished.')
            return

        # GPIO の現在の状態を再設定します。
        self._task_gpio.reset_state(self.name)

        phase_settings = self._settings.get_phase_settings()

        if phase_settings.reward_state_skip == 1:
            #self.results['state_result'] = TaskResult.Skipped
            self._logger.info(self.name + ': Skipped.')
            #wait_list = phase_settings.wait_time_list
            #wait_time = phase_settings.wait_time_in_s + wait_list[(self._settings.current_trial_num - 1) % len(wait_list)]
        
            return

        # 報酬を付与します。
        self._give_reward()

        self._logger.debug(self.name + ': Finished.')

    # 状態終了時に呼び出される State クラスの on_exit コールバックです。
    def exit(self, event_data):
        pass
    """
    # 報酬を付与します。
    def _give_reward(self):

        # 報酬用 LED を点灯します。
        self._task_gpio.switch_reward_led('ON')

        # 報酬用ブザーを鳴らします。
        #self._task_gpio.trigger_reward_buzzer()

        speaker.play_wav("/home/share/Operantbox_development/src/operant_conditioning_task/music/6000Hz_sin_wave.wav")

        # シリンジ ポンプを駆動します。
        self._task_gpio.trigger_reward_pump()

        # 報酬用 LED の点灯時間を調整します。
        time.sleep(5)

        # 報酬用 LED を消灯します。
        self._task_gpio.switch_reward_led('OFF')

        #WAVファイルの停止
        speaker.stop_wav()
    """

    def _give_reward(self):
        # 報酬用 LED を点灯します。
        self._task_gpio.switch_reward_led('ON')

        # 報酬用ブザーを鳴らします。
        #self._task_gpio.trigger_reward_buzzer()

        speaker.play_wav("/home/share/Operantbox_development/src/operant_conditioning_task/music/6000Hz_sin_wave.wav")

        # シリンジ ポンプを駆動します。
        self._task_gpio.trigger_reward_pump()

        # すべての動作が1秒間続くように待機します。
        time.sleep(1)

        # 報酬用 LED を消灯します。
        self._task_gpio.switch_reward_led('OFF')

        # ブザーの停止（もし必要であればコードを追加）
        #self._task_gpio.stop_reward_buzzer()

        # WAVファイルの停止（もし音声ファイルの再生があれば）
        speaker.stop_wav()

