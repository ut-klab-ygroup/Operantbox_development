#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" task_results.py
# 行動課題実験の結果データの保持とファイル保存を行います。
# また、結果データに基づく成績の判定も行います。
"""

import csv
import time

import numpy as np


class TaskResults:
    """
    行動課題実験の結果データの保持とファイル保存を行います。
    また、結果データに基づく成績の判定も行います。
    """

    def __init__(self, results_file_path):

        # 結果データを保存する CSV 形式ファイルを用意します。
        self.results_file = open(results_file_path, 'w', newline='')
        self._results_file_writer = csv.writer(self.results_file, delimiter=',')
        self._results_file_writer.writerow(['elapsed_time', 'trial_num', 'state_name', 'action', 'data1', 'data2'])

        # ===== インスタンス変数 =====

        # 実験の開始時刻 (UNIX 時間、sec) です。
        self._start_time = 0

        # Lick 行動の時系列データです。
        self._lick_results = dict()
        self._lick_results['elapsed_time'] = []     # 実験開始からの経過時間 (msec; int)
        self._lick_results['trial_num'] = []        # 試行番号 (int)
        self._lick_results['state_name'] = []       # 状態の名前 (str)
        self._lick_results['response_time'] = []    # キューの呈示から lick 行動までの反応時間 (msec)

        # Nose poke 行動の時系列データです。
        self._nose_poke_results = dict()
        self._nose_poke_results['elapsed_time'] = []    # 実験開始からの経過時間 (msec; int)
        self._nose_poke_results['trial_num'] = []       # 試行番号 (int)
        self._nose_poke_results['state_name'] = []      # 状態の名前 (str)
        self._nose_poke_results['target_num'] = []      # ターゲットの番号 (int)
        self._nose_poke_results['is_correct'] = []      # 正解/不正解 (bool)

        # 実験開始からの総試行数です。
        self._total_trials = 0

    # Lick 行動の結果を記録します。
    def store_lick_results(self, unix_time, trial_num, state_name, response_time):

        # 結果を保持します。
        elapsed_time = unix_time - self._start_time
        self._lick_results['elapsed_time'].append(elapsed_time)
        self._lick_results['trial_num'].append(trial_num)
        self._lick_results['state_name'].append(state_name)
        self._lick_results['response_time'].append(response_time)

        # 結果ファイルに保存します。
        self._results_file_writer.writerow([elapsed_time, trial_num, state_name, 'Lick', response_time, ''])

    # Nose poke 行動の結果を記録します。
    def store_nose_poke_results(self, unix_time, trial_num, state_name, target_num, is_correct):

        # 結果を保持します。
        elapsed_time = unix_time - self._start_time
        self._nose_poke_results['elapsed_time'].append(elapsed_time)
        self._nose_poke_results['trial_num'].append(trial_num)
        self._nose_poke_results['state_name'].append(state_name)
        self._nose_poke_results['target_num'].append(target_num)
        self._nose_poke_results['is_correct'].append(is_correct)

        # 結果ファイルに保存します。
        self._results_file_writer.writerow([elapsed_time, trial_num, state_name, 'Nose poke', target_num, is_correct])

    # 実験開始からの総試行数を 1 つ増やします。
    def increment_total_trials(self):
        self._total_trials += 1

    # 現在の試行から num_trials_before 回前までの lick 行動の結果を集計し、キューの呈示から lick 行動までの
    # 反応時間が response_time_threshold 秒以内である試行の割合が rate_threshold を超えるかどうか判定します。
    def check_lick_results(self, num_trials_before, response_time_threshold, rate_threshold):
        total_count = 0
        true_count = 0
        for response_time in reversed(self._lick_results['response_time']):
            if response_time <= response_time_threshold:
                true_count += 1
            total_count += 1

            if total_count == num_trials_before:
                return true_count / total_count > rate_threshold

        # 試行回数を満たしていない場合は、False を返します。
        return False

    # 現在の時刻から time_before 時間 (sec) 前までの nose poke 行動の結果を集計し、nose poke の回数が
    # num_nose_pokes_threshold を超えるかどうか判定します。
    def check_num_nose_pokes(self, time_before, num_nose_pokes_threshold):

        # 開始時間と終了時間を求めます。
        max_time = time.time() - self._start_time
        min_time = max_time - time_before

        # 開始時間を満たしていない場合は、False を返します。
        if min_time < 0:
            return False

        # 経過時間データにおいて、指定した時間範囲に対応するインデックス範囲を取得します。
        index_range = self._get_index_range_from_time_range(self._nose_poke_results['elapsed_time'], min_time, max_time)

        return index_range.shape[0] > num_nose_pokes_threshold

    # 現在の時刻から time_before 時間 (sec) 前までの nose poke 行動の結果を集計し、下記の条件 (A) あるいは (B) を
    # 満たすどうか判定します。
    # (A) accuracy > 50% かつ 正解回数 > 15
    # (B) 正解回数 > 30
    def check_nose_poke_results(self, time_before):

        # 開始時間と終了時間を求めます。
        max_time = time.time() - self._start_time
        min_time = max_time - time_before

        # 開始時間を満たしていない場合は False を返します。
        if min_time < 0:
            return False

        # 経過時間データにおいて、指定した時間範囲に対応するインデックス範囲を取得します。
        index_range = self._get_index_range_from_time_range(self._nose_poke_results['elapsed_time'], min_time, max_time)

        # 指定した時間範囲における正解数を求めます。
        total_count = 0
        correct_count = 0
        for i in index_range:
            if self._nose_poke_results['is_correct'][i]:
                correct_count += 1
            total_count += 1

        # 条件 (A): accuracy > 50% かつ 正解回数 > 15、あるいは (B): 正解回数 > 30 を満たすどうか判定します。
        if total_count == 0:
            return False
        else:
            return ((correct_count / total_count > 0.5) & (correct_count > 15)) | (correct_count > 30)

    # 経過時間データにおいて、指定した時間範囲に対応するインデックス範囲を取得します。
    def _get_index_range_from_time_range(self, elapsed_time_data, min_time, max_time):
        elapsed_time_data = np.array(elapsed_time_data)
        return np.where((elapsed_time_data >= min_time) & (elapsed_time_data <= max_time))[0]

    # 現在の総試行回数が total_trial_threshold を超えるかどうか判定します。
    def check_total_trials(self, total_trial_threshold):
        return self._total_trials > total_trial_threshold


# 設定フェーズの更新判定のテスト
if __name__ == '__main__':

    print('\nSetting phase update test: Started.')

    # 行動課題実験の結果データを保持するオブジェクトを生成します。
    task_results = TaskResults('./test_results.csv')

    # Lick 行動のダミー結果を記録します。
    for i in range(100):
        task_results.store_lick_results(i, i, 'LickState', i)

    # check_lick_results() メソッドをテストします。
    assert task_results.check_lick_results(101, 100, 0.5) is False
    assert task_results.check_lick_results(10, 20, 0.5) is False
    assert task_results.check_lick_results(100, 20, 0.5) is False
    assert task_results.check_lick_results(100, 49, 0.5) is False
    assert task_results.check_lick_results(100, 50, 0.5) is True
    assert task_results.check_lick_results(100, 51, 0.5) is True
    assert task_results.check_lick_results(10, 98, 0.89) is True

    # check_num_nose_pokes() メソッドをテストします。
    # ここでのテストは一度に試せないため、条件分岐しています。
    check_num_nose_pokes = True
    if check_num_nose_pokes:
        # 100 〜 199 秒のデータを入れ、余裕を持って 200 秒前からの条件で試します。
        for i in range(100):
            task_results.store_nose_poke_results(i + 100, i, 'NosePokeState', i % 2, i % 2 == 0)
        task_results._start_time = time.time()
        assert task_results.check_num_nose_pokes(200, 50) is False
        task_results._start_time = time.time() - 200
        assert task_results.check_num_nose_pokes(200, 20) is True
        assert task_results.check_num_nose_pokes(200, 99) is True
        assert task_results.check_num_nose_pokes(200, 100) is False
    # check_nose_poke_results() メソッドをいくつかのパターンでテストします。
    else:
        check_nose_poke_results = 0
        # 条件(A) を試します。
        if check_nose_poke_results == 0:
            # Nose poke 行動のダミー結果を記録します。
            for i in range(30):
                task_results.store_nose_poke_results(i + 100, i, 'NosePokeState', i % 2, i % 2 == 0)
            task_results._start_time = time.time() - 200
            assert task_results.check_nose_poke_results(200) is False
        # 条件(A) を試します。
        elif check_nose_poke_results == 1:
            for i in range(31):
                task_results.store_nose_poke_results(i + 100, i, 'NosePokeState', i % 2, i % 2 == 0)
            task_results._start_time = time.time() - 200
            assert task_results.check_nose_poke_results(200) is True
        # 条件(B) を試します。
        elif check_nose_poke_results == 2:
            for i in range(90):
                task_results.store_nose_poke_results(i + 100, i, 'NosePokeState', i % 3, i % 3 == 0)
            task_results._start_time = time.time() - 200
            assert task_results.check_nose_poke_results(200) is False
        # 条件(B) を試します。
        elif check_nose_poke_results == 3:
            for i in range(91):
                task_results.store_nose_poke_results(i + 100, i, 'NosePokeState', i % 3, i % 3 == 0)
            task_results._start_time = time.time() - 200
            assert task_results.check_nose_poke_results(200) is True

    # 実験開始からの総試行数を増やします。
    for i in range(100):
        task_results.increment_total_trials()

    # check_total_trials() メソッドをテストします。
    assert task_results.check_total_trials(100) is False
    task_results.increment_total_trials()
    assert task_results.check_total_trials(100) is True

    print('\nSetting phase update test: Passed.')
