#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" initial_state.py
試行の開始状態を処理します。
"""

from transitions import State


class InitialState(State):
    """
    試行の開始状態を処理します。
    transitions ライブラリの State クラスを継承します。
    """

    # 状態オブジェクトを生成します。
    def __init__(self, *args, **kwargs):

        # State クラスのコンストラクターを呼び出します。
        super(InitialState, self).__init__(kwargs['name'])

    # 状態開始時に呼び出される State クラスの on_enter コールバックです。
    def enter(self, event_data):
        pass

    # 状態終了時に呼び出される State クラスの on_exit コールバックです。
    def exit(self, event_data):
        pass
