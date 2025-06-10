import argparse as ap
import datetime
import sys

from phases.phase import Phase
from phases.phase1 import Phase1
from phases.phase2 import Phase2
from phases.phase3 import Phase3
from hardware.task_gpio import TaskGpio
from sampler import Sampler
import logger

phases = {
    '1': Phase1,
    '2': Phase2,
    '3': Phase3,
}

def main():
    commandline_parser = create_commandline_parser()
    args = commandline_parser.parse_args()

    if args.phase not in phases:
        print(f"フェーズの値が無効です: {phases.phase}")
        sys.exit(0)
    
    log = logger.create_logger(args.log_file_path)
    gpio = TaskGpio()
    sampler = Sampler(gpio, args.results_file_path)

    phase: Phase = phases[args.phase](gpio, log, sampler)

    try:
        phase.run()
    finally:
        sampler.cleanup()

def create_commandline_parser():
    description = 'operant_conditioning_task プログラムは、マウスのオペラント条件付け行動実験を行うプログラムです。'
    commandline_parser = ap.ArgumentParser(description=description)

    # 実験名
    current_datetime = datetime.datetime.now().strftime('%y%m%d-%H%M%S')
    commandline_parser.add_argument(
        '-n', '--name', dest='experiment_name', default=current_datetime,
        required=False,
        help='実験の名前です。指定しない場合は、現在の日時 (yymmdd-HHMMSS) をデフォルトの名前とします。'
    )

    # CSV形式の結果ファイル
    commandline_parser.add_argument(
        '-r', '--results', dest='results_file_path', default='./results_files/results-' + current_datetime + '.csv',
        required=False,
        help='CSV 形式の結果データ ファイル (*.csv) のパスです。'
             '指定しない場合は、ルート フォルダーに現在の日時 (results_<yymmdd-HHMMSS>.csv) でファイルを生成します。'
    )

    # ログファイル
    commandline_parser.add_argument(
        '-l', '--log', dest='log_file_path', default='./log_files/log-' + current_datetime + '.txt',
        required=False,
        help='テキスト形式のログ ファイル (*.txt) のパスです。'
             '指定しない場合は、ルート フォルダーに現在の日時 (log_<yymmdd-HHMMSS>.txt) でファイルを生成します。'
    )
    
    # フェーズ
    commandline_parser.add_argument(
        '-p', '--phase', dest='phase',
        required=True,
        help='開始フェーズの番号です。'
    )

    return commandline_parser

if __name__ == '__main__':
    main()
