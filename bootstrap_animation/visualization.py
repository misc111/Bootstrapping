"""
Visualization module for bootstrap animation
Creates beautiful Plotly figures for the Dash application
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple


class BootstrapVisualizer:
    """Creates and updates visualizations for bootstrap animation."""

    def __init__(self, metadata: Dict):
        """
        Initialize visualizer with triangle metadata.

        Parameters:
        -----------
        metadata : Dict
            Triangle metadata from AnimatedBootstrapODP.get_triangle_metadata()
        """
        self.metadata = metadata
        self.n_origin = metadata['n_origin']
        self.n_dev = metadata['n_dev']
        self.origin_labels = metadata['origin_labels']
        self.dev_labels = metadata['development_labels']

    def create_triangle_heatmap(
        self,
        data: np.ndarray,
        title: str,
        highlighted_cells: Optional[List[Tuple[int, int]]] = None,
        colorscale: str = 'Blues',
        value_divisor: float = 1.0,
        text_format: str = "{:,.0f}",
        hover_format: str = "{:,.0f}",
        colorbar_title: str = "Value",
        hover_suffix: str = ""
    ) -> go.Figure:
        """
        Create a heatmap visualization of a triangle.

        Parameters:
        -----------
        data : np.ndarray
            Triangle data to visualize
        title : str
            Figure title
        highlighted_cells : List[Tuple[int, int]], optional
            List of (origin, dev) cells to highlight
        colorscale : str
            Plotly colorscale name

        Returns:
        --------
        go.Figure
        """
        # Mask lower triangle (future periods)
        masked_data = np.array(data, dtype=float, copy=True)
        for i in range(self.n_origin):
            for j in range(self.n_dev):
                if i + j >= self.n_origin:
                    masked_data[i, j] = np.nan

        divisor = value_divisor if value_divisor not in (0, None) else 1.0
        scaled_data = masked_data / divisor

        text_data = np.empty(scaled_data.shape, dtype=object)
        hover_data = np.empty(scaled_data.shape, dtype=object)
        for i in range(self.n_origin):
            for j in range(self.n_dev):
                if np.isnan(scaled_data[i, j]):
                    text_data[i, j] = ''
                    hover_data[i, j] = ''
                else:
                    text_data[i, j] = text_format.format(scaled_data[i, j])
                    hover_value = hover_format.format(scaled_data[i, j])
                    hover_data[i, j] = f"{hover_value}{hover_suffix}"

        colorbar_title_to_use = colorbar_title
        if colorbar_title == "Value" and value_divisor == 1000:
            colorbar_title_to_use = "$000s"

        # Create base heatmap
        fig = go.Figure(data=go.Heatmap(
            z=scaled_data,
            x=self.dev_labels,
            y=self.origin_labels,
            colorscale=colorscale,
            text=text_data,
            customdata=hover_data,
            texttemplate='%{text}',
            textfont={"size": 10},
            hovertemplate='Origin: %{y}<br>Development: %{x}<br>Value: %{customdata}<extra></extra>',
            showscale=True,
            colorbar=dict(title=colorbar_title_to_use)
        ))

        # Reverse y-axis so oldest years are at top (ascending order going down)
        fig.update_yaxes(autorange="reversed")

        # Add highlighted cells overlay
        if highlighted_cells:
            for origin, dev in highlighted_cells:
                fig.add_shape(
                    type="rect",
                    x0=dev - 0.5, x1=dev + 0.5,
                    y0=origin - 0.5, y1=origin + 0.5,
                    line=dict(color="red", width=3),
                    fillcolor="rgba(255, 0, 0, 0.2)"
                )

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            xaxis_title="Development Period",
            yaxis_title="Accident Year",
            xaxis=dict(side='top'),  # Put x-axis labels on top
            height=400,
            template='plotly_white',
            font=dict(size=11)
        )

        return fig

    def create_residual_pool_scatter(
        self,
        residual_pool: List[Dict],
        highlighted_idx: Optional[int] = None
    ) -> go.Figure:
        """
        Create scatter plot of residual pool.

        Parameters:
        -----------
        residual_pool : List[Dict]
            List of residual dictionaries
        highlighted_idx : int, optional
            Index of residual to highlight

        Returns:
        --------
        go.Figure
        """
        residuals = [r['adjusted_residual'] for r in residual_pool]
        indices = list(range(len(residuals)))

        # Create colors: blue for normal, red for highlighted
        colors = ['#1f77b4'] * len(residuals)
        sizes = [8] * len(residuals)

        if highlighted_idx is not None:
            colors[highlighted_idx] = '#ff0000'
            sizes[highlighted_idx] = 15

        fig = go.Figure(data=go.Scatter(
            x=indices,
            y=residuals,
            mode='markers',
            marker=dict(
                color=colors,
                size=sizes,
                opacity=0.6,
                line=dict(width=1, color='white')
            ),
            text=[f"Origin {r['origin']}, Dev {r['dev']}<br>Residual: {r['adjusted_residual']:.2f}"
                  for r in residual_pool],
            hovertemplate='%{text}<extra></extra>'
        ))

        fig.update_layout(
            title=dict(text="Residual Pool", x=0.5, xanchor='center'),
            xaxis_title="Residual Index",
            yaxis_title="Adjusted Pearson Residual",
            height=300,
            template='plotly_white',
            showlegend=False
        )

        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        return fig

    def create_reserve_distribution(
        self,
        reserve_estimates: List[float],
        current_estimate: Optional[float] = None,
        base_reserve: Optional[float] = None
    ) -> go.Figure:
        """
        Create histogram of reserve estimates.

        Parameters:
        -----------
        reserve_estimates : List[float]
            List of reserve estimates from bootstrap iterations
        current_estimate : float, optional
            Current iteration's estimate to highlight
        base_reserve : float, optional
            Base chain ladder reserve estimate

        Returns:
        --------
        go.Figure
        """
        if len(reserve_estimates) == 0:
            # Empty plot
            fig = go.Figure()
            fig.update_layout(
                title="Reserve Distribution (No data yet)",
                xaxis_title="Reserve Estimate",
                yaxis_title="Frequency",
                height=350,
                template='plotly_white'
            )
            return fig

        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Histogram(
            x=reserve_estimates,
            nbinsx=30,
            name='Bootstrap Distribution',
            marker_color='rgba(99, 110, 250, 0.7)',
            hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
        ))

        # Add base reserve line
        if base_reserve is not None:
            fig.add_vline(
                x=base_reserve,
                line_dash="dash",
                line_color="green",
                annotation_text="Base CL",
                annotation_position="top"
            )

        # Add current estimate line
        if current_estimate is not None:
            fig.add_vline(
                x=current_estimate,
                line_dash="solid",
                line_color="red",
                annotation_text="Current",
                annotation_position="top"
            )

        fig.update_layout(
            title=dict(text=f"Reserve Distribution (n={len(reserve_estimates)})", x=0.5, xanchor='center'),
            xaxis_title="Reserve Estimate",
            yaxis_title="Frequency",
            height=350,
            template='plotly_white',
            showlegend=False
        )

        return fig

    def create_sampling_animation_frame(
        self,
        iteration_detail: Dict,
        frame_idx: int,
        show_triangle: bool = True
    ) -> go.Figure:
        """
        Create a single animation frame showing the sampling process.

        Parameters:
        -----------
        iteration_detail : Dict
            Iteration details from AnimatedBootstrapODP
        frame_idx : int
            Which sample in the sequence to show (0 to n_cells-1)
        show_triangle : bool
            Whether to show the bootstrap triangle being built

        Returns:
        --------
        go.Figure
        """
        sampling_details = iteration_detail['sampling_details']

        if frame_idx >= len(sampling_details):
            frame_idx = len(sampling_details) - 1

        # Get current sample
        current_sample = sampling_details[frame_idx]

        # Build partial bootstrap triangle up to this point
        partial_triangle = np.zeros((self.n_origin, self.n_dev))
        for i in range(min(frame_idx + 1, len(sampling_details))):
            sample = sampling_details[i]
            partial_triangle[sample['origin'], sample['dev']] = sample['bootstrap_value']

        # Mask unfilled cells
        for i in range(self.n_origin):
            for j in range(self.n_dev):
                if i + j >= self.n_origin or partial_triangle[i, j] == 0:
                    partial_triangle[i, j] = np.nan

        # Create heatmap with current cell highlighted
        divisor = 1000.0
        scaled_triangle = partial_triangle / divisor

        text_data = np.empty(scaled_triangle.shape, dtype=object)
        hover_data = np.empty(scaled_triangle.shape, dtype=object)
        for i in range(self.n_origin):
            for j in range(self.n_dev):
                if np.isnan(scaled_triangle[i, j]):
                    text_data[i, j] = ''
                    hover_data[i, j] = ''
                else:
                    text_data[i, j] = f"{scaled_triangle[i, j]:,.0f}"
                    hover_data[i, j] = f"{scaled_triangle[i, j]:,.0f} ($000s)"

        fig = go.Figure(data=go.Heatmap(
            z=scaled_triangle,
            x=self.dev_labels,
            y=self.origin_labels,
            colorscale='Purples',
            text=text_data,
            texttemplate='%{text}',
            textfont={"size": 10},
            showscale=True,
            customdata=hover_data,
            hovertemplate='Origin: %{y}<br>Development: %{x}<br>Value: %{customdata}<extra></extra>',
            colorbar=dict(title="$000s")
        ))

        # Reverse y-axis so oldest years are at top
        fig.update_yaxes(autorange="reversed")

        # Highlight current cell
        fig.add_shape(
            type="rect",
            x0=current_sample['dev'] - 0.5,
            x1=current_sample['dev'] + 0.5,
            y0=current_sample['origin'] - 0.5,
            y1=current_sample['origin'] + 0.5,
            line=dict(color="rgba(255, 215, 0, 1)", width=4),
            fillcolor="rgba(255, 215, 0, 0.3)"
        )

        # Add annotation for current sample
        format_thousands = lambda value: f"{value / 1000:,.0f}"

        annotation_text = (
            f"Cell ({current_sample['origin']}, {current_sample['dev']})<br>"
            f"Fitted: {format_thousands(current_sample['fitted'])} ($000s)<br>"
            f"Residual: {current_sample['sampled_residual']:.2f}<br>"
            f"Sampled from: ({current_sample['sampled_from_origin']}, {current_sample['sampled_from_dev']})<br>"
            f"Bootstrap: {format_thousands(current_sample['bootstrap_value'])} ($000s)"
        )

        fig.add_annotation(
            x=0.5,
            y=1.15,
            xref="paper",
            yref="paper",
            text=annotation_text,
            showarrow=False,
            font=dict(size=11, color="black"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="gray",
            borderwidth=1,
            borderpad=5
        )

        fig.update_layout(
            title=dict(
                text=f"Sampling Progress: {frame_idx + 1} / {len(sampling_details)}",
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="Development Period",
            yaxis_title="Accident Year",
            xaxis=dict(side='top'),  # Put x-axis labels on top
            height=500,
            template='plotly_white',
            font=dict(size=11)
        )

        return fig

    def create_statistics_panel(self, summary: Dict, current_iteration: int) -> go.Figure:
        """
        Create a panel showing statistics as they evolve.

        Parameters:
        -----------
        summary : Dict
            Summary statistics from bootstrap run
        current_iteration : int
            Current iteration number

        Returns:
        --------
        go.Figure
        """
        if len(summary['reserve_estimates']) == 0:
            return go.Figure()

        # Get rolling statistics
        reserves = summary['reserve_estimates'][:current_iteration + 1]

        if len(reserves) == 0:
            return go.Figure()

        fig = go.Figure()

        # Line plot of estimates over iterations
        fig.add_trace(go.Scatter(
            y=reserves,
            mode='lines',
            name='Reserve Estimate',
            line=dict(color='rgba(99, 110, 250, 0.5)', width=1),
            hovertemplate='Iteration: %{x}<br>Reserve: %{y:.0f}<extra></extra>'
        ))

        # Add rolling mean
        if len(reserves) > 10:
            rolling_mean = pd.Series(reserves).rolling(window=min(50, len(reserves))).mean()
            fig.add_trace(go.Scatter(
                y=rolling_mean,
                mode='lines',
                name='Rolling Mean',
                line=dict(color='red', width=2),
                hovertemplate='Rolling Mean: %{y:.0f}<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=f"Reserve Convergence (n={len(reserves)})", x=0.5, xanchor='center'),
            xaxis_title="Iteration",
            yaxis_title="Reserve Estimate",
            height=300,
            template='plotly_white',
            showlegend=True,
            legend=dict(x=0.7, y=1)
        )

        return fig
