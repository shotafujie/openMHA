# 07-single-channel-noise-reduction: 単一チャンネル雑音低減

> [English version](README.txt)

このサンプルは、雑音パワースペクトル密度に基づくケプストラム平滑化の適用方法を実演します。

使用する主なプラグインは `smooth_cepstrum` で、平滑化を行います。推定されたパワースペクトル密度（PSD）は AC 変数経由で入力として提供される必要があります。PSD 推定は `noise_psd_estimator` プラグインが行います。このプラグインは、推定された音声存在確率を使用したケプストラル領域音声生成モデルに基づく雑音パワースペクトル密度推定を行います。

## 参考文献

- Colin Breithaupt, Timo Gerkmann, Rainer Martin, "A Novel A Priori SNR Estimation Approach Based on Selective Cepstro-Temporal Smoothing", IEEE Int. Conf. Acoustics, Speech, Signal Processing, Las Vegas, NV, USA, Apr. 2008.
- Timo Gerkmann, Rainer Martin, "On the Statistics of Spectral Amplitudes After Variance Reduction by Temporal Cepstrum Smoothing and Cepstral Nulling", IEEE Trans. Signal Processing, Vol. 57, No. 11, pp. 4165-4174, Nov. 2009.
- Timo Gerkmann, Richard C. Hendriks, "Unbiased MMSE-based Noise Power Estimation with Low Complexity and Low Tracking Delay", IEEE Trans. Audio, Speech and Language Processing, Vol. 20, No. 4, pp. 1383-1393, May 2012.

## 特許

- Colin Breithaupt, Timo Gerkmann, Rainer Martin: "Spectral Smoothing Method for Noisy Signals", European Patent EP2158588B1 (Oct. 2010), Danish Patent DK2158588T3 (Feb. 2011), US Patent US8892431B2 (Nov. 2014).
- Timo Gerkmann, Rainer Martin: "Method for Determining Unbiased Signal Amplitude Estimates After Cepstral Variance Modification", US Patent US8208666B2 (Jun. 2012).
