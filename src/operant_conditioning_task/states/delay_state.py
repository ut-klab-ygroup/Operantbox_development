#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" delay_state.py
マウスの lick 課題成功後の待機状態を処理します。
"""

import time
import signal

from transitions import State

from states.task_result_enum import TaskResult
from state_machine.task_results import TaskResults #作業ディレクトリ的にできるか？
import functools

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
        self._task_gpio._detect_lick()
        self._task_gpio.reset_state(self.name)
        self._task_gpio._detect_lick()


        # 待機課題を監視します。
        self._monitor_wait_task(phase_settings)

        self._logger.debug(self.name + ': Finished')

    # 状態終了時に呼び出される State クラスの on_exit コールバックです。
    def exit(self, event_data):
        pass

    # 待機課題を監視します。
    

    def _signal_handler(self, signum, frame, wait_time, lick_time_list, start_time):
        # Check the elapsed time to determine if the monitoring period has finished.
        if time.perf_counter() - start_time > wait_time:#phase_settings.wait_time_in_s:
            # Stop the alarm timer.
            signal.setitimer(signal.ITIMER_REAL, 0)
            # Record the success and log it.
            self.results['state_result'] = TaskResult.Success
            self.results['lick_time_list'] = lick_time_list
            self._logger.info(f"{self.name}: Success")# with lick times: {lick_time_list}")
        else:
            # Check if a lick has been detected.
            #self._task_gpio._detect_lick()
            if self._task_gpio._lick_sensor.is_pressed:
                self._task_gpio._lick_time = time.time()
                self._task_gpio.get_lick_results(self.results)
                self._logger.info(self.name + ': Lick detected at ' + str(self.results['lick_time']))
                    ##lick_timeの検出は01で行っても良い。
                #lick_time_list.append(current_time - start_time)
                lick_time_list.append(self.results['lick_time'])
                self._task_gpio.reset_state(self.name) 
                    #reset_stateをここで行わないとlick_timeが更新されない。
                    #todo：調査@240602
                        ##→そもそもresultsを使わなければチャタリングの問題も生じなさそうで20hzでの検出も可能か？それかsignalハンドラーによる呼び出しそのものでチャタリング的なこと起こる？？
                #self._logger.info(f"{self.name}: Lick detected at {current_time - start_time} seconds")
                    #time.sleep(1)
            """
            if self._task_gpio.is_licked:
                #current_time = time.perf_counter()
                self._task_gpio.get_lick_results(self.results)
                self._logger.info(self.name + ': Lick detected at ' + str(self.results['lick_time']))
                #lick_time_list.append(current_time - start_time)
                lick_time_list.append(self.results['lick_time'])
                #self._logger.info(f"{self.name}: Lick detected at {current_time - start_time} seconds")
                self._task_gpio.reset_state(self.name)
                #self._task_gpio._detect_lick()
                #self._task_gpio.is_licked = False 
            """
            
            
            

    def _monitor_wait_task(self, phase_settings):
        # Turn off the chamber light.
        self._task_gpio.switch_chamber_light('OFF')
        start_time = time.perf_counter()
        wait_list = phase_settings.wait_time_list
        wait_time = phase_settings.wait_time_in_s + wait_list[(self._settings.current_trial_num - 1) % len(wait_list)]
        lick_time_list = []

        while time.perf_counter() - start_time <= wait_time:

            # Set the signal handler for SIGALRM.
            #handler = lambda signum, frame: self._signal_handler(signum, frame, self, wait_time, lick_time_list, start_time)
            handler = functools.partial(self._signal_handler, wait_time=wait_time, lick_time_list=lick_time_list, start_time=start_time)
            signal.signal(signal.SIGALRM, handler)

            # Configure the timer to fire every 0.1 seconds.
            signal.setitimer(signal.ITIMER_REAL, 0.1, 0.1)

            # Wait for the signal handler to end the monitoring.
            while signal.getitimer(signal.ITIMER_REAL)[0] != 0:
                time.sleep(0.1)  # Sleep to prevent high CPU usage, only wake to check if timer is still running.

# Note: This code assumes that `TaskResult` and `_task_gpio` are defined within the class that contains `_monitor_wait_task`.
    #この関数はおそらく削除で良い@240602
    def __monitor_wait_task(self, phase_settings):

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
            self._task_gpio.reset_state(self.name)
            self._task_gpio._detect_lick()
            if self._task_gpio.is_licked:
                self._task_gpio.get_lick_results(self.results)
                self._logger.info(self.name + ': Lick detected at ' + str(self.results['lick_time']))
                lick_time_list.append(self.results['lick_time'])
                # GPIO の現在の状態を再設定します。
                #この処理によって、resultsの中にlick_timeが格納される。
                #self._task_gpio.get_lick_results(self.results)
                #self._logger.info(self.name + 'Lick detected')
                #lick_time_list.append(self.results['lick_time'])
                time.sleep(0.01)
                self._task_gpio.reset_state(self.name)
                self._task_gpio._detect_lick()
                #この遅延時間については要検討, 一括操作可能になると良いか。
                time.sleep(0.01)
                #self.results['state_result'] = TaskResult.Success
                
            """
            2024/5/24 大石
            _task_gpio.is_licled はリックセンサーに反応があった時にTrueになるのですが、Falseにするのは読み出し側が行う必要があります。
            例えば lick_state.py では enter() の中で _task_gpio.reset_state() を呼び出して is_licked を False にしてから
            _monitor_lick_task() を行い, is_licked が True になるのを監視しています。
            このコードでは is_licked を False にしていないので毎ループで記録されてしまう可能性があります。
                →つまり永遠にlickが検出され続けてしまうということ。
                    -チャタリングの問題を解決する
                    -_task_gpioを外す？
                -いずれにせよ、一定期間におけるlickを全て検出する必要がある。
            is_licked が True になるたびに False にすればいいかというとセンサーのチャタリングなどの問題があるので単純にはいかなくて要検討です。

            to 大石さん
            コメントくださりありがとうございます。
            実験で使用するために、各trialで複数のlickを検出できるようにする必要があります。現在の稼働中の実験システムに合わせる場合、20hzオーダーでのlickの検出が求められます。そのようにするためのアイデアは何かおもちでしょうか。
            trial構造を変えて、stateをlick一回ごとに変えるのは、素人イメージ的にはcpuに負荷がかかりそうな気がしています。
            仮にそうだとして、現在ここのファイルで試みられているように一つのstateで行われたlick全てを検出するために、上述していただいたチャタリングの問題をうまく回避する方法はありますでしょうか。
            現状のtask_gpio.pyでは構造的に厳しいなどあればご指摘願いたいです。
            相談内容が多く、大変恐縮ですが、何卒よろしくお願いいたします。
            24/05/24            大久保 拝
            """
            time.sleep(0.001)

        self.results['state_result'] = TaskResult.Success
        self.results['lick_time_list'] = lick_time_list
        print(lick_time_list)
        self._logger.info(self.name + ': Success.')
