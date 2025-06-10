import logging

# ログ出力を行うオブジェクトを生成します。
# show_verbose_log=True の場合は DEBUG レベル以上、そうでない場合は、
# INFO レベル以上のログを標準出力に表示します。
# また、ログ ファイルのパスが指定されている場合は、show_verbose_log の設定に
# 関わらず、DEBUG レベル以上のログをテキスト ファイル (.txt) に保存します。
def create_logger(log_file_path=None, show_verbose_log=False):

    # ログの標準出力のハンドラーを生成します。
    # 詳細ログの表示が指定されている場合は、DEBUG レベル以上のログを標準出力に出します。
    # そうでない場合は、Info レベル以上のログを標準出力に出します。
    stream_handler = logging.StreamHandler()
    if show_verbose_log:
        stream_handler.setLevel(logging.DEBUG)
    else:
        stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    stream_handler.setFormatter(formatter)

    # ログ ファイルのパスが指定されている場合は、ファイル出力のハンドラーを生成します。
    # DEBUG レベル以上のログをファイルに保存します。
    if log_file_path:
        file_handler = logging.FileHandler(filename=log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

    # ログ出力を行うオブジェクトを生成します。
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    if log_file_path:
        logger.addHandler(file_handler)

    return logger
