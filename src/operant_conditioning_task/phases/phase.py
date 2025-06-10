# 各フェーズのクラスの親クラス. インターフェースを定義.

class Phase:
    def run(self):
        pass

    def get_trial(self) -> int:
        pass