#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" task_result_enum.py
課題の結果を示す列挙体です。
"""

from enum import Enum


class TaskResult(Enum):
    """
    課題の結果を示す列挙体です。
    """

    NotDecided = 0
    Success = 1
    Failure = 2
    Skipped = 3
    Timeout = 4
