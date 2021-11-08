#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" main.py
Raspberry Pi でマウスのオペラント条件付け行動課題実験を行う operant_conditioning_task
プログラムを開始します。
"""

import argparse as ap
import datetime
import sys

from gpio.task_gpio import TaskGpio
from settings.settings import Settings
from state_machine.task_results import TaskResults
from state_machine.operant_conditioning_model import OperantConditioningModel
import utility
from utility import OperantConditioningError, OperantConditioningSettingError

PROGRAM_NAME = 'operant_conditioning_task'
PROGRAM_VERSION = '211105'


# マウスのオペラント条件付け行動課題実験を行う operant_conditioning_task プログラムを開始します。
def main():

    # コマンドライン引数を取得します。
    commandline_parser = create_commandline_parser()
    args = commandline_parser.parse_args()

    try:
        # 設定ファイルを読み込み、設定オブジェクトを生成します。
        settings = Settings(args.experiment_name, args.setting_file_path)

        # ログ出力を行うオブジェクトを生成します。
        logger = utility.create_logger(args.log_file_path, settings.show_verbose_log)

        # Raspberry Pi の GPIO でデジタル入出力を行うオブジェクトを生成します。
        task_gpio = TaskGpio(settings.pin_assignment, logger)

        # 行動課題実験の結果データを保持するオブジェクトを生成します。
        task_results = TaskResults(args.results_file_path)

        # 行動課題実験を行うステート マシンのモデルを生成します。
        state_machine_model = OperantConditioningModel(args.experiment_name, settings, task_gpio,
                                                       task_results, logger)

        # InitialState を自己遷移 (InitialState->InitialState) することによって行動課題実験を開始します。
        logger.info(f'Program: "{PROGRAM_NAME}-{PROGRAM_VERSION}" started.')
        logger.info(f'Program: Setting file: {args.setting_file_path}.')
        state_machine_model.trigger('SetNextTrial')

    except KeyboardInterrupt:
        logger.info('Program: Stopped.')
        sys.exit(0)
    except OperantConditioningSettingError as exception:
        print(f'The following error occurred in the settings.\n{exception}')
        sys.exit(1)
    except OperantConditioningError as exception:
        logger.error(f'Program: The following error occurred.\n{exception}')
        sys.exit(1)
    except Exception as exception:
        logger.error(f'Program: The following error occurred.\n{exception}')
        sys.exit(1)
    else:
        logger.info('Program: Finished.')
    finally:
        try:
            task_results.results_file.close()
        except:
            pass


# コマンドライン引数のパーサーを生成します。
def create_commandline_parser():

    # プログラムの説明です。
    description = 'operant_conditioning_task プログラムは、マウスのオペラント条件付け行動実験を行うプログラムです。'

    # コマンドライン引数のパーサーを生成します。
    commandline_parser = ap.ArgumentParser(description=description)

    # 現在の日時の文字列 (yymmdd-HHMMSS) を取得します。
    current_datetime = datetime.datetime.now().strftime('%y%m%d-%H%M%S')

    # 実験名を指定する引数を追加します。
    commandline_parser.add_argument(
        '-n', '--name', dest='experiment_name', default=current_datetime,
        required=False,
        help='実験の名前です。指定しない場合は、現在の日時 (yymmdd-HHMMSS) をデフォルトの名前とします。'
    )

    # toml 形式の設定ファイルを指定する引数を追加します。
    commandline_parser.add_argument(
        '-s', '--setting', dest='setting_file_path', default='./settings/settings.toml',
        required=False,
        help='toml 形式の設定ファイル (*.toml) のパスです。'
             '指定しない場合は、settings フォルダーにある setting.toml ファイルをデフォルトの設定ファイルとします。'
    )

    # CSV 形式の結果データ ファイルを指定する引数を追加します。
    commandline_parser.add_argument(
        '-r', '--results', dest='results_file_path', default='./results_files/results-' + current_datetime + '.csv',
        required=False,
        help='CSV 形式の結果データ ファイル (*.csv) のパスです。'
             '指定しない場合は、ルート フォルダーに現在の日時 (results_<yymmdd-HHMMSS>.csv) でファイルを生成します。'
    )

    # ログ ファイルを指定する引数を追加します。
    commandline_parser.add_argument(
        '-l', '--log', dest='log_file_path', default='./log_files/log-' + current_datetime + '.txt',
        required=False,
        help='テキスト形式のログ ファイル (*.txt) のパスです。'
             '指定しない場合は、ルート フォルダーに現在の日時 (log_<yymmdd-HHMMSS>.txt) でファイルを生成します。'
    )

    return commandline_parser


# operant_conditioning_task プログラムのエントリー ポイントです。
if __name__ == '__main__':
    main()
