# NB06との違い
  ## hardware
    * NP反応時に点灯するライト, 報酬提供時のライトが赤色
    * NP holeのライトがやや明るいか(定量化前)

# 実験文書

## 全般情報

- **照明条件**: 実験全体を通じてハウスライトはオフ。
- **ブザー周波数**: 最低70Hz。
- **報酬メカニズム**: ブザーとライトが1秒間同時に作動。

## phase1

### 刺激と環境

- **報酬開始**: トライアル開始後5秒。
- **ライトの色**: 赤（やや明るめ、以前は豆電球を使用）。
- **トライアル持続時間**: トライアル間隔(ITI)は15-24秒の間で疑似ランダムに変化。

### センサー検出

- **リックセンサー**: 10Hzの頻度で反応を検出。

### データ出力

- **CSVファイル名**: `results_experiment_time`
- **内容に含まれるもの**: NP1-3、オペラント行動、トライアル開始時間など。

## phase2

### 刺激と環境

- **NPホール照明**: 5つのNPホールのうち中央3つを点灯（端の2つはテープで覆う）。
- **トライアル持続時間**: 各トライアルは60秒間。
- **オペラント条件**: 最初の3秒間に`OP_NP_correct`がなければ、それが記録され、報酬が与えられる。
- **ランダムITI**: 未実装、計画中。

### データ変換のための分析

- **CSVからCc.h5への変換**: nb06の実験構造を踏襲しつつ、CSVの内容に基づいて一部修正。

###　センサー検出

- **NPセンサー**: 反応を2Hzで含めて検出、10Hzへの変更を計画中。
- **検出の問題**: 高周波検出の課題に対する調整が進行中。

## パイプライン解析

- **パラメータ開発**: nb06の設定に合わせつつ、現在の実験設定に合わせてダウンサンプルレートなどを調整。

### オペラントデータ

- **アップサンプリング**: オペラントデータを10Hzでゼロ埋めアップサンプリング。
- **レスポンスマッピング**: レスポンスはトライアル開始からの時間差分に基づいて対応するインデックスにマップされる。

### 将来の実装

- **Zドライブへの転送**: 現在は手動で行っていますが、自動化を目指す。
- **エラー修正**: NPデータの記録の重複に対する修正を進行中。

## 追加ノート

- **データ検証の目的**: リックセンサーとNPセンサーの検出漏れや誤検出を確認する。
- **テスト方法**: ランダムITIを利用し、面積を0.25倍に減少させてテスト。

## バージョンとファイル取り扱い

- **ファイル名の手動変更**: 必要に応じて手動で変更されます。

# Experiment Documentation（English）

## General Information

- **Light Condition**: House light off throughout the experiments.
- **Buzzer Frequency**: Minimum 70 Hz.
- **Reward Mechanism**: Coincides with buzzer and light for 1 second.

## Phase 1: Initial Setup

### Stimulus and Environment

- **Reward Onset**: 5 seconds after the trial starts.
- **Light Color**: Red (slightly bright, previously used bulbs were incandescent).
- **Trial Duration**: Inter-Trial Interval (ITI) pseudo-randomly varies between 15-24 seconds.

### Sensor Detection

- **Lick Sensor**: Detection of responses at 10 Hz frequency.

### Data Output

- **CSV Filename**: `results_experiment_time`
- **Content Includes**: Actions like NP1-3, operant behaviors, trial start times.

### Changes and Implementations

- **Modifications**: Correspondence with nb06 still under confirmation.
- **Sensor Improvement**: Transition from high frequency detection challenges due to chatter issues, adjustments to 2 Hz detection under consideration.

## Phase 2: Advanced Setup

### Stimulus and Environment

- **NP Hole Illumination**: Middle three of five NP holes are lit; the outer two are covered with tape.
- **Trial Duration**: Each trial lasts 60 seconds.
- **Operant Condition**: If no `OP_NP_correct` in the first 3 seconds, it's recorded and rewarded.

### Data Output

- **Random ITI**: Not implemented yet but planned.

### Data Transformation for Analysis

- **CSV to Cc.h5**: Follows nb06's experiment structures with some modifications based on CSV contents.

### Sensor Detection

- **NP Sensor**: Includes responses at 2 Hz, planning to change to 10 Hz.
- **Detection Issues**: Ongoing adjustments to tackle high-frequency detection challenges.

### Pipeline Analysis

- **Parameter Development**: Matches settings from nb06 but tailored to the current experimental setup for parameters like downsample rates.

### Operational Data

- **Up-sampling**: Operant data upsampled to 10 Hz with zero padding.
- **Response Mapping**: Responses are mapped to their respective indices starting from trial start.

### Future Implementations

- **Z Drive Transfer**: Currently manual, intended to automate.
- **Error Corrections**: Ongoing fixes for recording overlaps in NP data.

## Additional Notes

- **Purpose of Data Verification**: To check for any missed detections or false detections in lick and NP sensors.
- **Testing Method**: Utilizing random ITI, with reduced area by 0.25 times.

## Version and File Handling

- **File Renaming**: Done manually as per the requirements.

    
