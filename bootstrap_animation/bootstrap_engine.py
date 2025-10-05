"""
Bootstrap Engine for Shapland ODP Bootstrap Methodology
Uses chainladder's BootstrapODPSample for correct implementation
"""

import numpy as np
import chainladder as cl
from chainladder import BootstrapODPSample
from typing import Dict, Optional


class AnimatedBootstrapODP:
    """
    Wrapper around chainladder's BootstrapODPSample with animation support.

    This class uses the chainladder library's built-in ODP bootstrap implementation
    and adds tracking/visualization features for animation.
    """

    def __init__(self, triangle_data: Optional[cl.Triangle] = None, random_state: int = 42):
        """
        Initialize the bootstrap engine.

        Parameters:
        -----------
        triangle_data : cl.Triangle, optional
            The loss triangle data. If None, loads the GenIns sample dataset.
        random_state : int
            Random seed for reproducibility
        """
        self.random_state = random_state

        # Load triangle data
        if triangle_data is None:
            self.triangle = cl.load_sample('genins')
        else:
            self.triangle = triangle_data

        # Fit base chain ladder model
        self.base_model = cl.Chainladder().fit(self.triangle)

        # Store incremental triangles for visualization
        self.actual_incremental = self.triangle.cum_to_incr()
        self.fitted_incremental = self.base_model.full_expectation_.cum_to_incr()

        # Slice to match original dimensions
        n_dev_orig = self.actual_incremental.shape[3]
        self.fitted_incremental = self.fitted_incremental.iloc[:, :, :, :n_dev_orig]

        # Storage for bootstrap results
        self.iteration_details = []
        self.reserve_estimates = []
        self.scale_parameter = None
        self.residual_pool = []  # Populated via residual preparation
        self._residual_adjusted_values = np.array([])
        self._prepare_residual_pool()

    def _calculate_base_reserve(self) -> float:
        """Calculate base reserve estimate from chain ladder."""
        ultimate = self.base_model.ultimate_.values[0, 0, :, -1]
        latest = self.triangle.latest_diagonal.values[0, 0, :, 0]
        return np.sum(ultimate - latest)

    def get_triangle_metadata(self) -> Dict:
        """Get metadata about the triangle for visualization."""
        n_origin = self.triangle.shape[2]
        n_dev = self.triangle.shape[3]

        return {
            'n_origin': n_origin,
            'n_dev': n_dev,
            'base_reserve': self._calculate_base_reserve(),
            'actual_cumulative': self.triangle.values[0, 0],
            'actual_incremental': self.actual_incremental.values[0, 0],
            'fitted_incremental': self.fitted_incremental.values[0, 0],
            'residuals': self._get_residuals(),
            'residual_pool': self.residual_pool,
            'origin_labels': [str(x) for x in self.triangle.origin.values],
            'development_labels': [str(x) for x in self.triangle.development.values]
        }

    def _prepare_residual_pool(self) -> None:
        """Prepare residual pool and related helpers for visualization."""
        actual = self.actual_incremental.values[0, 0]
        fitted = self.fitted_incremental.values[0, 0]

        with np.errstate(divide='ignore', invalid='ignore'):
            standardized_residuals = (actual - fitted) / np.sqrt(np.abs(fitted))
            standardized_residuals = np.nan_to_num(
                standardized_residuals, nan=0.0, posinf=0.0, neginf=0.0
            )

        self.unscaled_residuals = standardized_residuals

        n_origin, n_dev = standardized_residuals.shape
        residual_entries = []
        residual_values = []

        for origin in range(n_origin):
            for dev in range(n_dev):
                if origin + dev >= n_origin:
                    continue  # Outside observed triangle

                value = standardized_residuals[origin, dev]
                if fitted[origin, dev] <= 0 or not np.isfinite(value) or value == 0:
                    continue

                residual_entries.append({
                    'origin': origin,
                    'dev': dev,
                    'standardized_residual': value
                })
                residual_values.append(value)

        if not residual_entries:
            self.residual_pool = []
            self._residual_adjusted_values = np.array([])
            return

        residual_values = np.array(residual_values)
        mean_adjusted = float(np.mean(residual_values)) if residual_values.size else 0.0

        adjusted_values = []
        for entry in residual_entries:
            adjusted = entry['standardized_residual'] - mean_adjusted
            entry['adjusted_residual'] = adjusted
            adjusted_values.append(adjusted)

        self.residual_pool = residual_entries
        self._residual_adjusted_values = np.array(adjusted_values)

    def _get_residuals(self):
        """Return unscaled Pearson residuals for display."""
        return getattr(self, 'unscaled_residuals', None)

    def _find_residual_match(self, residual_value: float):
        """Find index and entry in residual pool matching residual_value."""
        if not self.residual_pool or self._residual_adjusted_values.size == 0:
            return None, None

        diffs = np.abs(self._residual_adjusted_values - residual_value)
        match_idx = int(np.argmin(diffs))
        match_entry = self.residual_pool[match_idx]
        # Provide graceful handling when difference is significantly large
        if not np.isfinite(diffs[match_idx]):
            return None, None
        return match_idx, match_entry

    def run_bootstrap(self, n_iterations: int = 1000) -> Dict:
        """
        Run bootstrap using chainladder's BootstrapODPSample.

        Parameters:
        -----------
        n_iterations : int
            Number of bootstrap iterations to run

        Returns:
        --------
        Dict containing summary statistics
        """
        # Use chainladder's bootstrap implementation
        bootstrap_sample = BootstrapODPSample(
            n_sims=n_iterations,
            random_state=self.random_state,
            hat_adj=False  # Use degrees of freedom adjustment
        ).fit(self.triangle)

        # Store scale parameter
        self.scale_parameter = bootstrap_sample.scale_

        # Get resampled triangles
        resampled_triangles = bootstrap_sample.resampled_triangles_

        # Process each bootstrap sample
        self.iteration_details = []
        self.reserve_estimates = []

        for i in range(n_iterations):
            # Get bootstrap triangle
            boot_tri = resampled_triangles.iloc[i]

            # Fit chain ladder and calculate reserve
            boot_model = cl.Chainladder().fit(boot_tri)
            ultimate = boot_model.ultimate_.values[0, 0, :, -1].sum()
            latest = boot_tri.latest_diagonal.values[0, 0, :, 0].sum()
            reserve = ultimate - latest

            self.reserve_estimates.append(reserve)

            # Store iteration details for animation
            boot_incr = boot_tri.cum_to_incr().values[0, 0]
            n_origin, n_dev = boot_incr.shape

            # Create sampling details (simplified - just show bootstrap values)
            sampling_details = []
            for ii in range(n_origin):
                for jj in range(n_dev):
                    if ii + jj < n_origin:
                        fitted_value = self.fitted_incremental.values[0, 0, ii, jj]
                        bootstrap_value = boot_incr[ii, jj]

                        if fitted_value > 0:
                            sampled_residual = (bootstrap_value - fitted_value) / np.sqrt(
                                np.abs(fitted_value)
                            )
                        else:
                            sampled_residual = 0.0

                        match_idx, match_entry = self._find_residual_match(sampled_residual)

                        sampling_details.append({
                            'origin': ii,
                            'dev': jj,
                            'fitted': fitted_value,
                            'bootstrap_value': bootstrap_value,
                            'sampled_from_origin': match_entry['origin'] if match_entry else None,
                            'sampled_from_dev': match_entry['dev'] if match_entry else None,
                            'sampled_residual': sampled_residual,
                            'sampled_residual_index': match_idx,
                            'sequence': len(sampling_details)
                        })

            self.iteration_details.append({
                'iteration': i,
                'bootstrap_incremental': boot_incr,
                'bootstrap_cumulative': boot_tri.values[0, 0],
                'reserve_estimate': reserve,
                'sampling_details': sampling_details
            })

        reserves = np.array(self.reserve_estimates)

        return {
            'n_iterations': n_iterations,
            'reserve_estimates': reserves,
            'mean': np.mean(reserves),
            'std': np.std(reserves),
            'min': np.min(reserves),
            'max': np.max(reserves),
            'percentiles': {
                '5': np.percentile(reserves, 5),
                '25': np.percentile(reserves, 25),
                '50': np.percentile(reserves, 50),
                '75': np.percentile(reserves, 75),
                '95': np.percentile(reserves, 95)
            }
        }

    def run_single_iteration(self, iteration_num: int):
        """
        Run a single bootstrap iteration.
        This is a simplified version that just runs the full bootstrap.
        For real-time animation, call run_bootstrap with n_iterations=1.
        """
        if len(self.iteration_details) <= iteration_num:
            # Need to run more iterations
            needed = iteration_num + 1 - len(self.iteration_details)
            self.run_bootstrap(needed)
