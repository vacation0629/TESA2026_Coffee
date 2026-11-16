from __future__ import annotations
from typing import Any

try:
    import numpy as np
    import xgboost as xgb
    HAS_XGB = True
except ImportError:  # pragma: no cover
    np = None  # type: ignore
    xgb = None  # type: ignore
    HAS_XGB = False


class EWMAFallbackPlugin:
    """Zero-dependency pure-Python residual tracker when xgboost is unavailable or under-sampled."""

    def __init__(self, alpha: float = 0.35) -> None:
        self.alpha = alpha
        self.buyer_residuals: dict[str, float] = {}

    def fit(self, rows: list[dict[str, Any]]) -> None:
        self.buyer_residuals.clear()
        for row in rows:
            b_id = str(row.get("buyer_id", ""))
            res = float(row.get("residual", 0.0))
            prev = self.buyer_residuals.get(b_id, 0.0)
            self.buyer_residuals[b_id] = self.alpha * res + (1.0 - self.alpha) * prev

    def predict_adjustment(self, features: dict[str, Any]) -> float:
        b_id = str(features.get("buyer_id", ""))
        return self.buyer_residuals.get(b_id, 0.0)


class OptionalXGBPlugin:
    """Pluggable shallow XGBoost predictor supporting MODE_A_RESIDUAL, MODE_B_WIN_PROB, MODE_C_WEIGHT_TUNER."""

    FEATURE_KEYS = ["cpr_t", "slope_t", "cv_t", "dir_t", "iur_t", "demand_sacks", "defect_ratio", "bean_size"]

    def __init__(self, xgb_cfg: dict[str, Any]) -> None:
        self.cfg = xgb_cfg
        self.mode: str = xgb_cfg.get("mode", "MODE_A_RESIDUAL")
        self.min_samples: int = int(xgb_cfg.get("min_samples", 18))
        self.fallback = EWMAFallbackPlugin()
        self.model: Any = None
        self.buyer_index: dict[str, int] = {}
        self.trained_samples: int = 0

    def is_ready(self) -> bool:
        return (
            bool(self.cfg.get("enabled", True))
            and HAS_XGB
            and self.model is not None
            and self.trained_samples >= self.min_samples
        )

    def _vectorize(self, row: dict[str, Any]) -> list[float]:
        b_id = str(row.get("buyer_id", "unknown"))
        if b_id not in self.buyer_index:
            self.buyer_index[b_id] = len(self.buyer_index)
        vec = [float(row.get(k, 0.0)) for k in self.FEATURE_KEYS]
        vec.append(float(self.buyer_index[b_id]))
        return vec

    def fit(self, history_rows: list[dict[str, Any]]) -> None:
        self.fallback.fit(history_rows)
        self.trained_samples = len(history_rows)
        if not (self.cfg.get("enabled", True) and HAS_XGB and self.trained_samples >= self.min_samples):
            self.model = None
            return

        X = np.array([self._vectorize(r) for r in history_rows], dtype=float)
        if self.mode == "MODE_B_WIN_PROB":
            y = np.array([1 if r.get("won", False) else 0 for r in history_rows], dtype=int)
            clf = xgb.XGBClassifier(
                max_depth=int(self.cfg.get("max_depth", 3)),
                n_estimators=int(self.cfg.get("n_estimators", 30)),
                learning_rate=float(self.cfg.get("learning_rate", 0.1)),
                eval_metric="logloss",
            )
            clf.fit(X, y)
            self.model = clf
        else:
            y = np.array([float(r.get("residual", 0.0)) for r in history_rows], dtype=float)
            reg = xgb.XGBRegressor(
                max_depth=int(self.cfg.get("max_depth", 3)),
                n_estimators=int(self.cfg.get("n_estimators", 30)),
                learning_rate=float(self.cfg.get("learning_rate", 0.1)),
            )
            reg.fit(X, y)
            self.model = reg

    def predict_price(self, v_i: float, p_heur: float, features: dict[str, Any]) -> tuple[float, bool]:
        """Returns (predicted_price, used_xgb_flag)."""
        if not self.is_ready():
            delta = self.fallback.predict_adjustment(features)
            return v_i * ((p_heur / max(1.0, v_i)) + delta), False

        x_vec = np.array([self._vectorize(features)], dtype=float)
        if self.mode == "MODE_B_WIN_PROB":
            best_price = p_heur
            best_ev = -1e9
            for mult in (0.96, 0.98, 1.00, 1.02, 1.04, 1.06):
                cand_price = p_heur * mult
                cand_feat = dict(features, cpr_t=cand_price / max(1.0, v_i))
                prob = float(self.model.predict_proba(np.array([self._vectorize(cand_feat)], dtype=float))[0][1])
                ev = (cand_price - v_i) * prob + (-0.20 * v_i) * (1.0 - prob)
                if ev > best_ev:
                    best_ev = ev
                    best_price = cand_price
            return best_price, True

        delta_m = float(self.model.predict(x_vec)[0])
        return p_heur + (v_i * delta_m), True
