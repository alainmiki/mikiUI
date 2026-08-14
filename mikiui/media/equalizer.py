"""Simple N-band equalizer for MikiUI.

Applies a single overall gain derived from the mean band gain (in dB) to a list
of float samples. Pure-Python, dependency-free.
"""


class Equalizer:
    """An N-band equalizer storing per-band gains in decibels (dB).

    The ``apply`` method derives one overall gain from the average of all band
    gains and multiplies every sample by it.
    """

    def __init__(self, bands: int = 3, default_gain: float = 0.0) -> None:
        """Create an equalizer with ``bands`` bands initialized to ``default_gain`` dB.

        Args:
            bands: Number of frequency bands (must be >= 1).
            default_gain: Initial gain in dB applied to every band.
        """
        if bands < 1:
            raise ValueError("bands must be >= 1")
        self._gains: list[float] = [float(default_gain) for _ in range(bands)]

    def set_band(self, i: int, gain_db: float) -> None:
        """Set the gain (dB) of band index ``i``.

        Args:
            i: Zero-based band index.
            gain_db: Gain in decibels.
        """
        self._gains[i] = float(gain_db)

    def get_band(self, i: int) -> float:
        """Return the gain (dB) of band index ``i``.

        Args:
            i: Zero-based band index.
        """
        return self._gains[i]

    def bands(self) -> list[float]:
        """Return a copy of all band gains (dB)."""
        return list(self._gains)

    def apply(self, samples: list[float]) -> list[float]:
        """Apply the equalizer to a list of samples.

        The overall gain is derived from the mean band gain using the formula
        ``factor = 10 ** (mean_gain_db / 20)`` (dB-to-linear conversion), and
        every sample is multiplied by ``factor``.

        Args:
            samples: List of float amplitudes (typically -1..1).

        Returns:
            A new list of scaled samples.
        """
        mean_gain = sum(self._gains) / len(self._gains)
        factor = 10 ** (mean_gain / 20)
        return [s * factor for s in samples]
