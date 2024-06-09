#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" settings.py
プログラム全体の設定を管理します。
"""

import numpy as np
import toml

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utility import OperantConditioningSettingError


class Settings:
    """
    プログラム全体の設定を管理します。
    また、toml 形式の設定ファイルを読み込み、対応する設定パラメーターを初期化します。
    """

    # 各設定パラメーターを初期化します。
    def __init__(self, experiment_name, setting_file_path):

        # ===== 設定ファイルで初期化されるパラメーター =====

        try:
            # 設定ファイルを読み込みます。
            settings_dict = toml.load(open(setting_file_path, encoding='utf-8'))

            # 設定フェーズの順番を名前で示したリストです。
            self._phase_list = settings_dict['phase_list']

            # 現在指定されている設定フェーズのリストにおけるインデックスです。
            self._current_phase_index = self._phase_list.index(settings_dict['current_phase'])

            # 設定フェーズ phase1 の更新判定の評価に用いる現在の試行からの試行回数です。
            self._num_trials_before = settings_dict['num_trials_before']

            # 設定フェーズ phase1 の更新判定の評価に用いるキューの呈示から lick 行動までの反応時間のクリア値 (sec) です。
            self._response_time_threshold = settings_dict['response_time_threshold']

            # 設定フェーズ phase1 の更新判定の評価に用いるキューの呈示から lick 行動までの反応時間をクリアした試行の割合です。
            self._rate_threshold = settings_dict['rate_threshold']

            # 設定フェーズ phase 5 と phase 6 の更新判定の評価に用いる試行数のクリア値です。
            self._trial_threshold_list = settings_dict['trial_threshold_list']

            # 各設定フェーズの設定パラメーターを PhaseSettings 型で格納した辞書です。
            # 設定フェーズ名をキーとします。
            self._phase_settings_dict = dict()
            for phase_name in self._phase_list:
                self._phase_settings_dict[phase_name] = PhaseSettings(settings_dict[phase_name])

        except Exception as exception:
            raise OperantConditioningSettingError(f'{type(exception)} {exception}.\n'
                                                  f'Please check the following setting file.\n{setting_file_path}')

        # ===== 固定の設定パラメーター =====

        # nose poke に使用するターゲットの番号です。
        self.NOSE_POKE_TARGETS = np.array([4, 3, 2, 1, 0])

        # Raspberry Pi の GPIO の端子の割り当てです。
        self.pin_assignment = dict()
        self.pin_assignment['chamber_light'] = 20
        self.pin_assignment['lick_sensor'] = 16
        self.pin_assignment['nose_poke_leds'] = [26, 19, 13, 6, 5]
        self.pin_assignment['nose_poke_sensors'] = [24, 23, 18, 15, 14]
        self.pin_assignment['reward_led'] = 21
        self.pin_assignment['reward_buzzer'] = 2
        self.pin_assignment['reward_pump'] = 7

        # ===== その他の設定パラメーター =====

        # 実験の名前です。
        self.experiment_name = experiment_name

        # 現在の試行番号です。
        self.current_trial_num = 0

        # 現在の設定フェーズにおける試行番号です。
        self._trial_num_in_phase = 0

        # 指定した試行回数で実験を停止します。
        # -1 の場合は、無制限です。
        self.num_trials_per_experiment = -1

        # 実験の停止要求を示すフラグです。
        self.cancel_flag = False

        # 詳細なログ情報をコンソールに出力するかどうかのフラグです。
        self.show_verbose_log = False

        # ===== デバッグ用設定 =====

        # ステート マシンのスケルトンをデバッグ実行するため、各状態の具体的な処理をスキップします。
        self.debug = dict()
        self.debug['skip_state'] = False

    # 現在指定されているフェーズ設定を PhaseSettings オブジェクト型で取得します。
    def get_phase_settings(self):
        return self._phase_settings_dict[self._phase_list[self._current_phase_index]]

    # 現在の設定フェーズにおける試行番号に対応する正解 nose poke ターゲットのインデックス リストを取得します。
    def get_correct_target_index_list(self):
        phase_settings = self.get_phase_settings()
        available_correct_targets = np.in1d(self.NOSE_POKE_TARGETS,
                                            phase_settings.x[(self._trial_num_in_phase - 1) % len(phase_settings.x)])
        return np.where(available_correct_targets)[0]

    # 次の試行のための設定を行います。
    def set_for_next_trial(self, experiment_results):

        # 試行の成績に基づいて、次の設定フェーズを設定します。
        settings_phase_name, go_to_next_phase = self._set_settings_phase(experiment_results)

        # 現在の試行番号を 1 つ増やします。
        self.current_trial_num += 1

        # フェーズ設定が更新される場合は、フェーズにおける試行番号を 1 にリセットします。
        # そうでない場合は、フェーズにおける試行番号を 1 つ増やします。
        if go_to_next_phase:
            self._trial_num_in_phase = 1
        else:
            self._trial_num_in_phase += 1

        return settings_phase_name

    # 試行の成績に基づいて、次の設定フェーズの設定します。
    # 設定フェーズの名前と、設定フェーズが変更されたかどうかのフラグを返します。
    def _set_settings_phase(self, experiment_results):

        go_to_next_phase = False
        if self._current_phase_index == 0:
            go_to_next_phase = experiment_results.check_lick_results(self._num_trials_before,
                                                                     self._response_time_threshold,
                                                                     self._rate_threshold)
        elif self._current_phase_index in {1, 2}:
            go_to_next_phase = experiment_results.check_num_nose_pokes(3600, 15)
        elif self._current_phase_index == 3:
            go_to_next_phase = experiment_results.check_nose_poke_results(3600)
        elif self._current_phase_index == 4:
            go_to_next_phase = experiment_results.check_total_trials(self._trial_threshold_list[0])
        elif self._current_phase_index == 5:
            go_to_next_phase = experiment_results.check_total_trials(self._trial_threshold_list[1])
        elif self._current_phase_index == 6:
            go_to_next_phase = experiment_results.check_total_trials(self._trial_threshold_list[2])
        elif self._current_phase_index == 7:
            go_to_next_phase = experiment_results.check_total_trials(self._trial_threshold_list[3])
        elif self._current_phase_index == 8:
            go_to_next_phase = experiment_results.check_total_trials(self._trial_threshold_list[4])
        elif self._current_phase_index == 9:
            go_to_next_phase = experiment_results.check_total_trials(self._trial_threshold_list[5])
        else:
            pass

        if go_to_next_phase:
            self._current_phase_index += 1

        return self._phase_list[self._current_phase_index], go_to_next_phase


class PhaseSettings:
    """
    1 つの設定フェーズの設定パラメーターを保持します。
    """

    def __init__(self, phase_settings_dict):
        self.x = phase_settings_dict['x']
        self.is_nose_poke_skip = phase_settings_dict['is_nose_poke_skip']
        self.is_lick_wait = phase_settings_dict['is_lick_wait']
        self.delay_state_skip = phase_settings_dict['delay_state_skip']
        self.reward_state_skip =phase_settings_dict['reward_state_skip']
        self.is_perservative = phase_settings_dict['is_perservative']
        self.wait_time_in_s = phase_settings_dict['wait_time_in_s']
        self.wait_time_list = phase_settings_dict['wait_time_list']
        self.timeout_in_s = phase_settings_dict['timeout_in_s']
        self.stimulus_duration_in_s = phase_settings_dict['stimulus_duration_in_s']
        self.limited_hold_in_s = phase_settings_dict['limited_hold_in_s']


# 設定クラスのテスト
if __name__ == '__main__':

    # 設定ファイルのパスを指定し、設定オブジェクトを生成します。
    setting_file_path = './settings.toml'
    settings = Settings('test', setting_file_path)

    # 各設定パラメーターをコンソールに出力します。
    print('\n[Setting parameters]')
    for key, val in vars(settings).items():
        if key == '_phase_settings_dict':
            for phase_name, phase_settings in val.items():
                print(f'{phase_name} = [x = {phase_settings.x}, is_nose_poke_skip = {phase_settings.is_nose_poke_skip}, '
                      f'is_lick_wait = {phase_settings.is_lick_wait},delay_state_skip = {phase_settings.delay_state_skip},reward_state_skip = {phase_settings.reward_state_skip}, is_perservative = {phase_settings.is_perservative}, '
                      f'wait_time_in_s = {phase_settings.wait_time_in_s}, timeout_in_s = {phase_settings.timeout_in_s}, '
                      f'limited_hold_in_s = {phase_settings.limited_hold_in_s}, '
                      f'stimulus_duration_in_s = {phase_settings.stimulus_duration_in_s}]')
        else:
            print(f'{key} = {val}')
