"""
Bootstrap Engine for Shapland ODP Bootstrap Methodology
Uses chainladder's BootstrapODPSample with additional tracking for animation
"""

import numpy as np
import pandas as pd
import chainladder as cl
from chainladder import BootstrapODPSample
from typing import Dict, List, Tuple, Optional


class AnimatedBootstrapODP:
    """
    Custom wrapper around chainladder's BootstrapODPSample that exposes
    intermediate steps for visualization and animation.
    """

    def __init__(self, triangle_data: Optional[cl.Triangle] = None, random_state: int = 42):
        """
        Initialize the bootstrap engine.

        Parameters:
        -----------
        triangle_data : chainladder.Triangle, optional
            Loss triangle data. If None, uses sample data.
        random_state : int
            Random seed for reproducibility
        """
        self.random_state = random_state
        np.random.seed(random_state)

        # Load data
        if triangle_data is None:
            self.triangle = cl.load_sample('genins')
        else:
            self.triangle = triangle_data

        # Fit base chain ladder model
        self.base_model = cl.Chainladder().fit(self.triangle)

        # Get LDFs from base model
        base_ldfs = self.base_model.ldf_.values[0, 0, 0, :]

        # Build fitted cumulative triangle by back-filling using LDFs
        # Start with the latest diagonal and divide by LDFs to fill in the historical triangle
        fitted_cumulative = np.zeros_like(self.triangle.values[0, 0])
        latest_diag = self.triangle.latest_diagonal.values[0, 0, :, 0]
        n_origin, n_dev = fitted_cumulative.shape

        # Fill the fitted triangle
        for i in range(n_origin):
            # Start with the latest diagonal value
            latest_dev_idx = n_origin - i - 1  # Last observed development period for this origin
            if latest_dev_idx < n_dev:
                fitted_cumulative[i, latest_dev_idx] = latest_diag[i]

                # Back-fill by dividing by LDFs
                for j in range(latest_dev_idx - 1, -1, -1):
                    if j < len(base_ldfs) and base_ldfs[j] > 0:
                        fitted_cumulative[i, j] = fitted_cumulative[i, j + 1] / base_ldfs[j]
                    else:
                        fitted_cumulative[i, j] = fitted_cumulative[i, j + 1]

        # Convert to incremental
        self.actual_incremental = self.triangle.cum_to_incr()
        fitted_incremental = np.diff(fitted_cumulative, axis=1, prepend=0)

        # Store as Triangle object for consistency
        fitted_tri = self.triangle.copy()
        fitted_tri.values = fitted_incremental.reshape(1, 1, *fitted_incremental.shape)
        self.fitted_incremental = fitted_tri

        # Calculate Pearson residuals
        self._calculate_residuals()

        # Storage for bootstrap iterations
        self.bootstrap_samples = []
        self.reserve_estimates = []
        self.iteration_details = []

    def _calculate_residuals(self):
        """Calculate unscaled and adjusted Pearson residuals."""
        # Get incremental values as arrays
        actual = self.actual_incremental.values[0, 0]  # Shape: (origin, dev)
        fitted = self.fitted_incremental.values[0, 0]

        # Unscaled Pearson residuals: (actual - fitted) / sqrt(fitted)
        with np.errstate(divide='ignore', invalid='ignore'):
            self.unscaled_residuals = (actual - fitted) / np.sqrt(fitted)
            self.unscaled_residuals = np.nan_to_num(self.unscaled_residuals, nan=0.0, posinf=0.0, neginf=0.0)

        # Get non-zero residuals for sampling (exclude structural zeros in lower triangle)
        self.residual_pool = []
        n_origin = actual.shape[0]
        n_dev = actual.shape[1]

        for i in range(n_origin):
            for j in range(n_dev):
                # Only include values in upper triangle where we have actual data
                # Exclude zero residuals as per Shapland (where actual == fitted)
                if i + j < n_origin and fitted[i, j] > 0 and self.unscaled_residuals[i, j] != 0:
                    self.residual_pool.append({
                        'origin': i,
                        'dev': j,
                        'residual': self.unscaled_residuals[i, j],
                        'fitted': fitted[i, j]
                    })

        # Calculate adjustment factor for degrees of freedom
        n = len(self.residual_pool)
        p = n_dev - 1  # Number of development factors estimated
        self.df = max(n - p, 1)

        # Apply degrees of freedom adjustment to create adjusted residuals
        adjustment = np.sqrt(n / self.df)
        for item in self.residual_pool:
            item['adjusted_residual'] = item['residual'] * adjustment

        # FIX 1: Center the adjusted residuals to ensure unbiased bootstrap
        # This is CRITICAL - the mean of sampled residuals must be zero
        mean_adjusted = np.mean([item['adjusted_residual'] for item in self.residual_pool])
        for item in self.residual_pool:
            item['adjusted_residual'] -= mean_adjusted

        # Calculate scale parameter (phi) for process variance (optional - for Fix 2)
        # Per Shapland formula 3.17: phi = sum(Pearson_residual^2) / degrees_of_freedom
        sum_squared_residuals = sum([item['residual']**2 for item in self.residual_pool])
        self.scale_parameter = sum_squared_residuals / self.df

    def run_single_iteration(self, iteration_num: int) -> Dict:
        """
        Run a single bootstrap iteration with detailed tracking.

        Returns:
        --------
        Dict containing:
            - sampled_residuals: List of (origin, dev, sampled_residual_value)
            - bootstrap_triangle: The generated bootstrap triangle
            - reserve_estimate: The estimated reserve for this iteration
        """
        np.random.seed(self.random_state + iteration_num)

        # Track sampling details
        sampling_details = []

        # Get array dimensions
        n_origin = self.actual_incremental.values[0, 0].shape[0]
        n_dev = self.actual_incremental.values[0, 0].shape[1]

        # Create bootstrap incremental triangle
        bootstrap_incremental = np.zeros((n_origin, n_dev))
        fitted = self.fitted_incremental.values[0, 0]

        # Sample residuals and generate bootstrap values for HISTORICAL triangle only
        for i in range(n_origin):
            for j in range(n_dev):
                if i + j < n_origin and fitted[i, j] > 0:
                    # Sample a residual with replacement
                    sampled = np.random.choice(len(self.residual_pool))
                    sampled_residual = self.residual_pool[sampled]['adjusted_residual']

                    # Generate bootstrap value: fitted + residual * sqrt(fitted)
                    bootstrap_value = fitted[i, j] + sampled_residual * np.sqrt(fitted[i, j])
                    bootstrap_value = max(0, bootstrap_value)  # Ensure non-negative

                    bootstrap_incremental[i, j] = bootstrap_value

                    # Track this sample
                    sampling_details.append({
                        'origin': i,
                        'dev': j,
                        'fitted': fitted[i, j],
                        'sampled_residual': sampled_residual,
                        'sampled_from_origin': self.residual_pool[sampled]['origin'],
                        'sampled_from_dev': self.residual_pool[sampled]['dev'],
                        'bootstrap_value': bootstrap_value,
                        'sequence': len(sampling_details)
                    })

        # Convert to cumulative
        bootstrap_cumulative = np.cumsum(bootstrap_incremental, axis=1)

        # Create chainladder Triangle object from bootstrap historical data
        bootstrap_tri = self.triangle.copy()
        bootstrap_tri.values = bootstrap_cumulative.reshape(1, 1, *bootstrap_cumulative.shape)

        # Fit NEW chain ladder model to bootstrap triangle and project to ultimate
        bootstrap_model = cl.Chainladder().fit(bootstrap_tri)

        # FIX 2: Add process variance to future incremental payments
        # Get full projection with future periods
        full_projection = bootstrap_model.full_triangle_.values[0, 0]
        full_incremental = np.diff(full_projection, axis=1, prepend=0)

        # Calculate reserve by summing future payments with Gamma noise
        reserve = 0.0
        for i in range(n_origin):
            latest_dev_idx = n_origin - i - 1  # Last observed diagonal position

            # Sum future incremental payments with process variance
            for j in range(latest_dev_idx + 1, full_projection.shape[1]):
                if not np.isnan(full_incremental[i, j]) and full_incremental[i, j] > 0:
                    expected_payment = full_incremental[i, j]

                    # Add process variance via Gamma distribution
                    # mean = expected_payment, variance = expected_payment * phi
                    # Gamma params: shape = mean/phi, scale = phi
                    shape = expected_payment / self.scale_parameter
                    scale = self.scale_parameter
                    actual_payment = np.random.gamma(shape, scale)

                    reserve += actual_payment

        result = {
            'iteration': iteration_num,
            'sampling_details': sampling_details,
            'bootstrap_incremental': bootstrap_incremental,
            'bootstrap_cumulative': bootstrap_cumulative,
            'reserve_estimate': reserve
        }

        self.iteration_details.append(result)
        self.reserve_estimates.append(reserve)

        return result

    def run_bootstrap(self, n_iterations: int = 1000) -> Dict:
        """
        Run complete bootstrap simulation.

        Parameters:
        -----------
        n_iterations : int
            Number of bootstrap iterations to run

        Returns:
        --------
        Dict containing summary statistics and all iteration details
        """
        self.iteration_details = []
        self.reserve_estimates = []

        for i in range(n_iterations):
            self.run_single_iteration(i)

        reserves = np.array(self.reserve_estimates)

        return {
            'n_iterations': n_iterations,
            'reserve_estimates': reserves,
            'mean': np.mean(reserves),
            'std': np.std(reserves),
            'percentiles': {
                '5': np.percentile(reserves, 5),
                '25': np.percentile(reserves, 25),
                '50': np.percentile(reserves, 50),
                '75': np.percentile(reserves, 75),
                '95': np.percentile(reserves, 95)
            },
            'iteration_details': self.iteration_details
        }

    def get_triangle_metadata(self) -> Dict:
        """Get metadata about the triangle for visualization setup."""
        n_origin = self.actual_incremental.values[0, 0].shape[0]
        n_dev = self.actual_incremental.values[0, 0].shape[1]

        return {
            'n_origin': n_origin,
            'n_dev': n_dev,
            'origin_labels': list(self.triangle.origin.astype(str)),
            'development_labels': list(self.triangle.development.astype(str)),
            'actual_incremental': self.actual_incremental.values[0, 0],
            'fitted_incremental': self.fitted_incremental.values[0, 0],
            'residuals': self.unscaled_residuals,
            'residual_pool': self.residual_pool,
            'base_reserve': self._calculate_base_reserve()
        }

    def _calculate_base_reserve(self) -> float:
        """Calculate base reserve estimate from chain ladder."""
        ultimate = self.base_model.ultimate_.values[0, 0, :, -1]
        latest = self.triangle.latest_diagonal.values[0, 0, :, 0]
        return np.sum(ultimate - latest)
