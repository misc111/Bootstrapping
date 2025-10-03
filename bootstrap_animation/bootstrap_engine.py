"""
Bootstrap Engine for Shapland ODP Bootstrap Methodology
Implements the Over-Dispersed Poisson bootstrap with detailed tracking
for animation purposes.
"""

import numpy as np
import pandas as pd
import chainladder as cl
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
        self.fitted_values = self.base_model.full_triangle_

        # Get expected values (fitted from GLM) for residual calculation
        # full_expectation_ gives the model's expected values, not just filled historicals
        expected_values = self.base_model.full_expectation_

        # Calculate incremental triangles
        self.actual_incremental = self.triangle.cum_to_incr()
        fitted_incremental_full = expected_values.cum_to_incr()

        # Slice fitted incremental to match original triangle dimensions
        # (fitted may have extra development periods from projection)
        n_dev_orig = self.actual_incremental.shape[3]
        self.fitted_incremental = fitted_incremental_full.iloc[:, :, :, :n_dev_orig]

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
                if i + j < n_origin and fitted[i, j] > 0:
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

        # Adjusted residuals
        adjustment = np.sqrt(n / self.df)
        for item in self.residual_pool:
            item['adjusted_residual'] = item['residual'] * adjustment

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

        # Sample residuals and generate bootstrap values
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

        # Convert to cumulative and create triangle
        bootstrap_cumulative = np.cumsum(bootstrap_incremental, axis=1)

        # Create chainladder Triangle object by copying structure
        bootstrap_tri = self.triangle.copy()
        bootstrap_tri.values = bootstrap_cumulative.reshape(1, 1, *bootstrap_cumulative.shape)

        # Fit chain ladder and calculate reserve
        bootstrap_model = cl.Chainladder().fit(bootstrap_tri)
        ultimate = bootstrap_model.ultimate_.values[0, 0, :, -1]
        latest = bootstrap_tri.latest_diagonal.values[0, 0, :, 0]
        reserve = np.sum(ultimate - latest)

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
