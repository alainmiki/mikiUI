"""Pure-Python audio filter helpers for MikiUI.

All filters operate on lists of float samples (amplitude roughly -1..1) and
return new lists. Outputs are clamped to the [-1, 1] range.
"""


def _clamp(value: float) -> float:
    """Clamp a value into the [-1, 1] range."""
    if value < -1.0:
        return -1.0
    if value > 1.0:
        return 1.0
    return value


class Filters:
    """A collection of simple, dependency-free audio filters.

    Every method returns a new list and leaves the input unchanged.
    """

    @staticmethod
    def gain(samples: list[float], db: float) -> list[float]:
        """Apply a linear gain expressed in decibels to each sample.

        Args:
            samples: List of float amplitudes.
            db: Gain in decibels (0 = unchanged).

        Returns:
            A new list of scaled, clamped samples.
        """
        factor = 10 ** (db / 20)
        return [_clamp(s * factor) for s in samples]

    @staticmethod
    def normalize(samples: list[float]) -> list[float]:
        """Scale samples so the peak absolute amplitude becomes 1.0.

        Args:
            samples: List of float amplitudes.

        Returns:
            A new list normalized to [-1, 1]; empty input returns empty list.
        """
        if not samples:
            return []
        peak = max(abs(s) for s in samples)
        if peak == 0.0:
            return [0.0 for _ in samples]
        return [_clamp(s / peak) for s in samples]

    @staticmethod
    def low_pass(samples: list[float], cutoff: float) -> list[float]:
        """One-pole low-pass filter (simple smoothing).

        ``cutoff`` in 0..1 controls smoothing: 0 = no smoothing (passthrough),
        1 = heavy smoothing (output approaches the running average). Uses the
        recursion ``y[n] = y[n-1] + alpha * (x[n] - y[n-1])`` with
        ``alpha = 1 - cutoff``.

        Args:
            samples: List of float amplitudes.
            cutoff: Smoothing amount in 0..1.

        Returns:
            A new list of smoothed samples.
        """
        alpha = 1.0 - float(cutoff)
        out: list[float] = []
        prev = 0.0
        for s in samples:
            prev = prev + alpha * (s - prev)
            out.append(_clamp(prev))
        return out

    @staticmethod
    def high_pass(samples: list[float], cutoff: float) -> list[float]:
        """High-pass filter: keep the part removed by ``low_pass``.

        Computed as ``samples - low_pass(samples, cutoff)``, emphasizing rapid
        changes while attenuating slow trends.

        Args:
            samples: List of float amplitudes.
            cutoff: Smoothing amount in 0..1 (see ``low_pass``).

        Returns:
            A new list of clamped samples.
        """
        low = Filters.low_pass(samples, cutoff)
        return [_clamp(s - l) for s, l in zip(samples, low)]
