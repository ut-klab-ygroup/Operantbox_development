import numpy as np
from scipy.io.wavfile import write

# 生成する波のパラメータ
sample_rate = 44100  # サンプルレート (Hz)
duration = 20        # 音の継続時間 (秒)
frequency = 880      # 正弦波の周波数 (Hz)

# 時間軸を生成
t = np.arange(0, duration, 1/sample_rate)

# 440Hzの正弦波を生成
sin_wave = 0.5 * np.sin(2 * np.pi * frequency * t)

# 波形をWAVファイルとして保存
write('880Hz_sin_wave.wav', sample_rate, sin_wave)