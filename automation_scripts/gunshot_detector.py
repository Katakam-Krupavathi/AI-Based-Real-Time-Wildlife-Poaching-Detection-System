# gunshot_detector.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import tensorflow as tf
import config

SAMPLE_RATE = 22050
DURATION = 2
SAMPLES = SAMPLE_RATE * DURATION
N_MELS = 64

_model = None
_train_mean = None
_train_std = None

def focal_loss(gamma=2., alpha=0.25):
    def loss(y_true, y_pred):
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1 - epsilon)
        pt = tf.where(tf.equal(y_true, 1), y_pred, 1 - y_pred)
        return -tf.reduce_mean(alpha * tf.pow(1 - pt, gamma) * tf.math.log(pt))
    return loss

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(config.GUNSHOT_MODEL_PATH):
            raise FileNotFoundError(f"Gunshot model not found at {config.GUNSHOT_MODEL_PATH}")
        _model = tf.keras.models.load_model(
            config.GUNSHOT_MODEL_PATH,
            custom_objects={"loss": focal_loss(), "focal_loss": focal_loss()}
        )
    return _model

def get_norm_stats():
    global _train_mean, _train_std
    if _train_mean is None or _train_std is None:
        if os.path.exists(config.MEAN_PATH) and os.path.exists(config.STD_PATH):
            _train_mean = np.load(config.MEAN_PATH)
            _train_std = np.load(config.STD_PATH)
        else:
            # Fallback default statistics for dB log-mel spectrogram features
            _train_mean = np.float32(-40.0)
            _train_std = np.float32(20.0)
    return _train_mean, _train_std

def detect_gunshot(audio_path, threshold=0.55):
    """
    Analyzes an audio file and returns (is_gunshot: bool, probability: float).
    """
    import librosa

    model = get_model()
    train_mean, train_std = get_norm_stats()

    y_audio, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)

    if len(y_audio) > SAMPLES:
        y_audio = y_audio[:SAMPLES]
    else:
        y_audio = np.pad(y_audio, (0, SAMPLES - len(y_audio)))

    mel = librosa.feature.melspectrogram(y=y_audio, sr=sr, n_mels=N_MELS)
    log_mel = librosa.power_to_db(mel, ref=np.max)
    delta = librosa.feature.delta(log_mel)
    delta2 = librosa.feature.delta(log_mel, order=2)

    features = np.stack([log_mel, delta, delta2], axis=-1)
    features = (features - train_mean) / train_std
    features = np.expand_dims(features, axis=0)

    prob = float(model.predict(features, verbose=0)[0][0])

    return prob > threshold, prob