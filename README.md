# 目的
Raspberry PiとArduinoを組み合わせてstandaloneで行動実験系を制御する

*コード：Operantbox_developmentのブランチ：feature/okubo_phase1-2
https://github.com/ut-klab-ygroup/Operantbox_development/tree/feature/okubo_phase1-2
コンセプト
状態遷移モデルを改変し、phaseごとに特定のstateにて実験を行い、他のstateをskip。
遷移図
->[trial]:Lick_state->delay_state->nose_poke_state->reward_state->[next trial]:Lick_state->….
コード概略
Src
Operant_conditioning_task
Operant_conditioning_task.py：制御ファイル
Gpio
センサー関連
Music
スピーカー
Settings
Settings.toml：実験phase,また、phaseごとの設定を行う
settings.py：
States
各stateでの動作を規定
States_machine
Task_results.py：結果の記録
Operant_conditioning_model.py：遷移を規定
Phase1：delay stateを利用し、そのほかのstateをskip
https://github.com/ut-klab-ygroup/Operantbox_development/blob/feature/okubo_phase1-2/src/operant_conditioning_task/states/delay_state.py
Phase2：nose_poke_stateを利用し、そのほかのstateをskip
https://github.com/ut-klab-ygroup/Operantbox_development/blob/feature/okubo_phase1-2/src/operant_conditioning_task/states/nose_poke_state.py
パイプライン用の変換：居室PCで行うことを想定
https://github.com/ut-klab-ygroup/Operantbox_development/tree/feature/okubo_phase1-2/rasp_preprocess_for_pipeline
