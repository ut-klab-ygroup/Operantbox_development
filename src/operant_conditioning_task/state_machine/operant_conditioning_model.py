#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" operant_conditioning_model.py
マウスのオペラント条件付け行動課題実験を行うステート マシンのモデルです。
"""

import time

from transitions import Machine

# ステート マシンで使用する状態が定義されたモジュールです。
from states.initial_state import InitialState
from states.lick_state import LickState
from states.delay_state import DelayState
from states.nose_poke_state import NosePokeState
from states.reward_state import RewardState
from states.timeout_state import TimeoutState

from states.task_result_enum import TaskResult
from utility import OperantConditioningError


class OperantConditioningModel:
    """
    マウスのオペラント条件付け行動課題実験を行うステート マシンのモデルです。
    """

    # transitions ライブラリの Machine クラスを用いて、ステート マシンを生成します。
    def __init__(self, name, settings, task_gpio, task_results, logger):

        # モデル オブジェクトの名前です。
        # 実験名をモデル名とします。
        self.name = name

        # プログラム全体の設定です。
        self.settings = settings

        # 行動課題実験の結果データを保持するオブジェクトです。
        self.task_results = task_results

        # ログ出力を行うオブジェクトです。
        self.logger = logger

        # ステート マシンの各状態を処理するオブジェクトを生成します。
        # 状態オブジェクトは、transitions ライブラリの State クラスの派生クラスから生成されます。
        states = [
            InitialState(name='InitialState'),
            LickState(name='LickState', settings=settings, task_gpio=task_gpio, logger=logger),
            DelayState(name='DelayState', settings=settings, task_gpio=task_gpio, logger=logger),
            NosePokeState(name='NosePokeState', settings=settings, task_gpio=task_gpio, logger=logger),
            RewardState(name='RewardState', settings=settings, task_gpio=task_gpio, logger=logger),
            TimeoutState(name='TimeoutState', settings=settings, task_gpio=task_gpio, logger=logger)
        ]

        # 状態遷移を定義します。
        # 遷移によって呼び出されるコールバック メソッドは、本クラスの [遷移コールバック メソッド] 以下に定義します。
        transitions = [
            {'trigger': 'SetNextTrial', 'source': ['InitialState', 'NosePokeState', 'RewardState', 'TimeoutState'],
             'dest': 'InitialState', 'after': 'start_trial'},
            {'trigger': 'StartTrial', 'source': 'InitialState', 'dest': 'LickState',
             'after': 'set_transition_after_lick_state'},
            {'trigger': 'LickState->DelayState', 'source': 'LickState', 'dest': 'DelayState',
             'after': 'set_transition_after_delay_state'},
            {'trigger': 'DelayState->NosePokeState', 'source': 'DelayState', 'dest': 'NosePokeState',
             'after': 'set_transition_after_nose_poke_state'},
            {'trigger': 'NosePokeState->RewardState', 'source': 'NosePokeState', 'dest': 'RewardState',
             'after': 'go_to_next_trial'},
            {'trigger': 'Timeout', 'source': ['LickState', 'DelayState', 'NosePokeState'], 'dest': 'TimeoutState',
             'after': 'go_to_next_trial'}
        ]

        # 状態処理オブジェクトと状態遷移のリストを渡して、ステート マシンを生成します。
        self.state_machine = Machine(model=self, states=states, transitions=transitions, initial=states[0],
                                     auto_transitions=False, ordered_transitions=False,
                                     send_event=True, queued=False)

    # ===== 遷移コールバック メソッド =====

    # 試行を開始します。
    def start_trial(self, event):
        # 実験開始時刻を記録します。
        if event.transition.source == 'InitialState':
            self.task_results.start_time = time.time()
            self.logger.info(f'Experiment: "{self.name}" started.')

        # 次の試行のための設定を行います。
        settings_phase_name = self.settings.set_for_next_trial(self.task_results)
        self.logger.info(f'Trial#{self.settings.current_trial_num}: Started., Setting phase: {settings_phase_name}')

        # 次の状態に遷移します。
        self.trigger('StartTrial')

    # LickState の結果を取得して、次の状態に遷移します。
    def set_transition_after_lick_state(self, event):

        # LickState オブジェクトでない場合はエラーを出します。
        if not isinstance(event.state, LickState):
            raise OperantConditioningError('This is not a LickState object.')

        # LickState の結果を取得します。
        results = event.state.results

        # 次の状態に遷移します。
        if results['state_result'] == TaskResult.Success:
            # Lick 行動の結果を記録します。
            try:
                response_time = results['lick_time'] - results['light_on_time']
                self.task_results.store_lick_results(results['lick_time'], self.settings.current_trial_num,
                                                     'LickState', response_time)
            except Exception as exception:
                if not self.settings.debug['skip_state']:
                    self.logger.error('Lick results cannot be obtained properly.')

            self.trigger('LickState->DelayState')
        elif results['state_result'] == TaskResult.Failure:
            self.trigger('Timeout')
        elif results['state_result'] == TaskResult.Skipped:
            self.trigger('LickState->DelayState')
        else:
            raise OperantConditioningError('The results of LickState are something wrong.')

    # DelayState の結果を取得して、次の状態に遷移します。
    def set_transition_after_delay_state(self, event):

        # DelayState オブジェクトでない場合はエラーを出します。
        if not isinstance(event.state, DelayState):
            raise OperantConditioningError('This is not a DelayState object.')

        # DelayState の結果を取得します。
        delay_state_results = event.state.results

        # 次の状態に遷移します。
        if delay_state_results['state_result'] == TaskResult.Success:
            self.trigger('DelayState->NosePokeState')
        elif delay_state_results['state_result'] == TaskResult.Failure:
            self.trigger('Timeout')
        else:
            raise OperantConditioningError('The results of DelayState are something wrong.')

    # NosePokeState の結果を取得して、次の状態に遷移します。
    def set_transition_after_nose_poke_state(self, event):

        # NosePokeStateオブジェクトでない場合はエラーを出します。
        if not isinstance(event.state, NosePokeState):
            raise OperantConditioningError('This is not a NosePokeState object.')

        # NosePokeState の結果を取得します。
        results = event.state.results

        # 次の状態に遷移します。
        if results['state_result'] in [TaskResult.Success, TaskResult.Failure]:
            # Nose poke 行動の結果を記録します。
            try:
                self.task_results.store_nose_poke_results(results['nose_poke_time'],
                                                          self.settings.current_trial_num,
                                                          'NosePokeState', results['target_num'],
                                                          results['is_correct'])
            except Exception as exception:
                if not self.settings.debug['skip_state']:
                    self.logger.error('Lick results cannot be obtained properly.')

            if results['state_result'] == TaskResult.Success:
                self.trigger('NosePokeState->RewardState')
            else:
                self.trigger('Timeout')
        elif results['state_result'] == TaskResult.Skipped:
            self.trigger('NosePokeState->RewardState')
        elif results['state_result'] == TaskResult.Timeout:
            self.trigger('SetNextTrial')
        else:
            raise OperantConditioningError('The results of NosePokeState are something wrong.')

    # 次の試行に移ります。
    def go_to_next_trial(self, event):
        self.logger.info(f'Trial#{self.settings.current_trial_num}: Finished.')

        # 実験の停止要求があった場合は次の試行に移らず、実験を終了します。
        if self.settings.cancel_flag:
            self.finalize_experiment()
            return
        # 試行回数が指定されており、かつその試行回数に到達した場合は、実験を終了します。
        elif self.settings.num_trials_per_experiment != -1 and \
                self.settings.current_trial_num >= self.settings.num_trials_per_experiment:
            self.finalize_experiment()
            return

        # 実験開始からの総試行数を 1 つ増やします。
        self.task_results.increment_total_trials()

        if self.settings.debug['skip_state']:
            time.sleep(2)

        # 次の状態に遷移します。
        self.trigger('SetNextTrial')

    # 実験終了時の処理を行います。
    def finalize_experiment(self):
        self.logger.info('Experiment: Finished.')

    # 状態クラスの単体テスト用の after コールバックです。
    def after_callback_for_test(self, event):
        try:
            results = event.state.results
            print('Results:', results)
        except:
            pass
        self.logger.info('Unit state test: After callback finished.')


# ===== テスト =====

# 各状態の具体的な処理をスキップして、ステート マシンのスケルトンをテスト実行します。
def test_state_machine_skeleton():

    import sys
    from settings.settings import Settings
    from state_machine.task_results import TaskResults
    from utility import create_logger

    try:
        # 設定ファイルを読み込み、設定オブジェクトを生成します。
        settings = Settings('test', '../settings/settings.toml')

        # 各状態の具体的な処理をスキップするように設定します。
        settings.debug['skip_state'] = True

        # 試行回数を設定します。
        settings.num_trials_per_experiment = 3

        # 空の GPIO のデジタル入出力を行うオブジェクトを生成します。
        task_gpio = None

        # 行動課題実験の結果データを保持するオブジェクトを生成します。
        task_results = TaskResults('./test_results.csv')

        # ログ出力を行うオブジェクトを生成します。
        logger = create_logger('./test_log.txt', True)

        # 行動課題実験を行うステート マシンのモデルを生成します。
        state_machine_model = OperantConditioningModel('test', settings, task_gpio, task_results, logger)

        # テストする状態を自己遷移 (tested_state_name->tested_state_name) することによって行動課題実験を開始します。
        logger.info('Program: Started.')
        state_machine_model.trigger('SetNextTrial')

    except KeyboardInterrupt:
        logger.info('Skeleton test: Stopped.')
        sys.exit(0)
    except OperantConditioningError as exception:
        logger.info(f'Skeleton test: The following OperantConditioningError occurred.\n{exception}')
        sys.exit(1)
    except Exception as exception:
        logger.error(f'Skeleton test: The following error occurred.\n{exception}')
        sys.exit(1)
    else:
        logger.info('Skeleton test: Passed.')


# tested_state_name で指定した単一の状態クラスをテスト実行します。
def test_unit_state(tested_state_name):

    import sys
    from settings.settings import Settings
    from state_machine.task_results import TaskResults
    from gpio.task_gpio import TaskGpio
    from utility import create_logger

    try:
        # 設定ファイルを読み込み、設定オブジェクトを生成します。
        settings = Settings('test', '../settings/settings.toml')

        # ログ出力を行うオブジェクトを生成します。
        logger = create_logger('./test_log.txt', True)

        # GPIO のデジタル入出力を行うオブジェクトを生成します。
        task_gpio = TaskGpio(settings.pin_assignment, logger)

        # 行動課題実験の結果データを保持するオブジェクトを生成します。
        task_results = TaskResults('./test_results.csv')

        # 行動課題実験を行うステート マシンのモデルを生成します。
        state_machine_model = OperantConditioningModel('test', settings, task_gpio, task_results, logger)

        # テストする状態を自己遷移 (tested_state_name->tested_state_name) することによって行動課題実験を開始します。
        logger.info(f'Unit state test: State "{tested_state_name}" started.')
        state_machine_model.state_machine.set_state(tested_state_name)
        state_machine_model.state_machine.add_transition(trigger='Test', source=tested_state_name,
                                                         dest=tested_state_name, after='after_callback_for_test')
        state_machine_model.trigger('Test')

    except KeyboardInterrupt:
        logger.info('Unit state test: Stopped.')
        sys.exit(0)
    except OperantConditioningError as exception:
        logger.info(f'Unit state test: The following OperantConditioningError occurred.\n{exception}')
        sys.exit(1)
    except Exception as exception:
        logger.error(f'Unit state test: The following error occurred.\n{exception}')
        sys.exit(1)
    else:
        logger.info(f'Unit state test: State "{tested_state_name}" passed.')


# ステート マシンのテスト
if __name__ == "__main__":

    # 状態クラスの名前を指定して、単一の状態クラスをテスト実行します。
    unit_state_test = True
    if unit_state_test:
        test_unit_state('DelayState')
    # ステート マシンのスケルトンをテスト実行します。
    else:
        test_state_machine_skeleton()
