import numpy as np
import scipy.io as sio
from scipy.optimize import least_squares


TRUST_SCALE = 4.0
REJECT_SCALE = 3.0
NUM_ITER = 3
MIN_OUTLIER_WEIGHT = 0.05
HUBER_SCALE = 5.0


def huber_localization(d, BS_positions, x0=None, weights=None):
    if x0 is None:
        x0 = np.mean(BS_positions, axis=1)

    if weights is None:
        weights = np.ones_like(d)

    def residual_func(x):
        diff = BS_positions - x.reshape(2, 1)
        pred_d = np.sqrt(np.sum(diff ** 2, axis=0))
        residual = pred_d - d
        return np.sqrt(weights) * residual

    result = least_squares(
        residual_func,
        x0,
        loss="huber",
        f_scale=HUBER_SCALE,
        max_nfev=100
    )

    return result.x


def compute_weights_and_corrected_distance(d, BS_positions, pos):
    diff = BS_positions - pos.reshape(2, 1)
    pred_d = np.sqrt(np.sum(diff ** 2, axis=0))

    residual = pred_d - d

    med = np.median(residual)

    mad = np.median(
        np.abs(residual - med)
    )

    mad = max(mad, 1e-6)

    deviation = np.abs(
        residual - med
    )

    trust = 1.0 / (
        1.0 + (
            deviation /
            (TRUST_SCALE * mad)
        ) ** 2
    )

    mask = deviation <= (
        REJECT_SCALE * mad
    )

    weights = trust.copy()

    weights[~mask] = MIN_OUTLIER_WEIGHT

    if np.sum(mask) < 4:
        weights = trust

    d_corrected = d + med
    d_corrected = np.maximum(
        d_corrected,
        1e-6
    )

    return weights, d_corrected


def your_algorithm(d, BS_positions):
    d = np.asarray(d, dtype=float).reshape(-1)

    pos = huber_localization(
        d,
        BS_positions
    )

    current_d = d.copy()

    for _ in range(NUM_ITER):
        weights, corrected_d = compute_weights_and_corrected_distance(
            current_d,
            BS_positions,
            pos
        )

        pos = huber_localization(
            corrected_d,
            BS_positions,
            x0=pos,
            weights=weights
        )

        current_d = corrected_d

    return pos


def main():
    mat_path = "DH_FR1.mat"

    data = sio.loadmat(
        mat_path,
        squeeze_me=False
    )

    BS_positions = np.asarray(
        data["BS_positions"],
        dtype=float
    )

    d_hat = np.asarray(
        data["d_hat"],
        dtype=float
    )

    p = np.asarray(
        data["p"],
        dtype=float
    )

    num_user = d_hat.shape[1]

    p_hat = np.zeros(
        (2, num_user)
    )

    for u in range(num_user):
        p_hat[:, u] = your_algorithm(
            d_hat[:, u],
            BS_positions
        )

    return p_hat


if __name__ == "__main__":
    main()