"""
Callback functions for Dash application
Handles interactivity and state management
"""

from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from typing import Dict, Optional
import time


def register_callbacks(app, bootstrap_engine, visualizer):
    """
    Register all callbacks for the Dash application.

    Parameters:
    -----------
    app : dash.Dash
        The Dash application instance
    bootstrap_engine : AnimatedBootstrapODP
        The bootstrap engine instance
    visualizer : BootstrapVisualizer
        The visualizer instance
    """

    @app.callback(
        [
            Output('iteration-store', 'data'),
            Output('play-button', 'children'),
            Output('play-button', 'color'),
        ],
        [
            Input('play-button', 'n_clicks'),
            Input('reset-button', 'n_clicks'),
            Input('run-all-button', 'n_clicks'),
        ],
        [
            State('iteration-store', 'data'),
            State('n-iterations-slider', 'value'),
        ],
        prevent_initial_call=True
    )
    def control_playback(play_clicks, reset_clicks, run_all_clicks, store_data, n_iterations):
        """Handle play/pause/reset button clicks."""
        if store_data is None:
            store_data = {
                'is_playing': False,
                'current_iteration': 0,
                'current_frame': 0,
                'n_iterations': n_iterations,
                'bootstrap_complete': False
            }

        triggered_id = ctx.triggered_id

        if triggered_id == 'reset-button':
            # Reset everything - clear bootstrap engine data
            bootstrap_engine.iteration_details = []
            bootstrap_engine.reserve_estimates = []
            return {
                'is_playing': False,
                'current_iteration': 0,
                'current_frame': 0,
                'n_iterations': n_iterations,
                'bootstrap_complete': False
            }, 'Play', 'success'

        elif triggered_id == 'run-all-button':
            # Run all iterations without animation
            if len(bootstrap_engine.iteration_details) < n_iterations:
                bootstrap_engine.run_bootstrap(n_iterations)

            return {
                'is_playing': False,
                'current_iteration': n_iterations - 1,
                'current_frame': 0,
                'n_iterations': n_iterations,
                'bootstrap_complete': True
            }, 'Play', 'success'

        elif triggered_id == 'play-button':
            # Toggle play/pause
            new_is_playing = not store_data.get('is_playing', False)

            if new_is_playing and not store_data.get('bootstrap_complete', False):
                # Start playing - run bootstrap if not already done
                if len(bootstrap_engine.iteration_details) < n_iterations:
                    # Run all bootstrap iterations (computation happens here)
                    bootstrap_engine.run_bootstrap(n_iterations)
                    store_data['bootstrap_complete'] = True

            store_data['is_playing'] = new_is_playing
            store_data['n_iterations'] = n_iterations

            button_text = 'Pause' if new_is_playing else 'Play'
            button_color = 'warning' if new_is_playing else 'success'

            return store_data, button_text, button_color

        raise PreventUpdate

    @app.callback(
        Output('interval-component', 'disabled'),
        [Input('iteration-store', 'data')]
    )
    def control_interval(store_data):
        """Enable/disable interval component based on play state."""
        if store_data is None:
            return True
        return not store_data.get('is_playing', False)

    @app.callback(
        Output('interval-component', 'interval'),
        [Input('speed-slider', 'value')]
    )
    def update_interval_speed(speed_value):
        """
        Update animation speed based on slider.
        Speed slider: 0.1x to 10x
        Interval: milliseconds per frame

        At high speeds, we need much higher minimum intervals because:
        - Creating 4 Plotly figures per update is expensive
        - Dash state management adds overhead
        - Browser needs time to render and respond
        """
        # Base interval: 300ms per frame at 1x speed (increased from 200ms)
        base_interval = 300

        # Calculate interval based on speed
        interval = int(base_interval / speed_value)

        # Set aggressive minimums to prevent overwhelming the browser
        # These minimums account for the cost of creating multiple Plotly figures
        if speed_value >= 7:
            min_interval = 100  # At 7-10x, minimum 100ms (10 fps max)
        elif speed_value >= 5:
            min_interval = 80   # At 5-7x, minimum 80ms (12.5 fps max)
        elif speed_value >= 3:
            min_interval = 60   # At 3-5x, minimum 60ms (16.7 fps max)
        elif speed_value >= 2:
            min_interval = 50   # At 2-3x, minimum 50ms (20 fps max)
        else:
            min_interval = 40   # Below 2x, minimum 40ms (25 fps max)

        return max(min_interval, interval)

    @app.callback(
        [
            Output('iteration-store', 'data', allow_duplicate=True),
            Output('main-triangle-graph', 'figure'),
            Output('residual-pool-graph', 'figure'),
            Output('distribution-graph', 'figure'),
            Output('statistics-graph', 'figure'),
            Output('progress-text', 'children'),
            Output('stats-text', 'children'),
        ],
        [
            Input('interval-component', 'n_intervals'),
            Input('step-button', 'n_clicks'),
            Input('iteration-store', 'data'),
        ],
        [
            State('show-cell-animation', 'value'),
        ],
        prevent_initial_call=True
    )
    def update_visualization(n_intervals, step_clicks, store_data, show_cell_anim):
        """Update all visualizations based on current state."""
        if store_data is None:
            raise PreventUpdate

        # Get state
        current_iteration = store_data.get('current_iteration', 0)
        current_frame = store_data.get('current_frame', 0)
        n_iterations = store_data.get('n_iterations', 0)
        is_playing = store_data.get('is_playing', False)
        bootstrap_complete = store_data.get('bootstrap_complete', False)

        # If reset was clicked (no iterations but store exists), show empty state
        if len(bootstrap_engine.iteration_details) == 0:
            # Return empty/initial visualizations
            empty_triangle = visualizer.create_triangle_heatmap(
                bootstrap_engine.actual_incremental.values[0, 0],
                "Bootstrap Triangle - Ready to start",
                colorscale='Purples',
                value_divisor=1000,
                colorbar_title="$000s"
            )
            empty_residual = visualizer.create_residual_pool_scatter(
                bootstrap_engine.residual_pool
            )
            empty_dist = visualizer.create_reserve_distribution(
                [],
                base_reserve=bootstrap_engine._calculate_base_reserve()
            )
            empty_stats = visualizer.create_statistics_panel(
                {'reserve_estimates': []},
                0
            )
            return store_data, empty_triangle, empty_residual, empty_dist, empty_stats, "Ready to start", ""

        # If bootstrap not complete, prevent update unless from store change
        if not bootstrap_complete and ctx.triggered_id != 'iteration-store':
            raise PreventUpdate

        # Check if we need to animate cell-by-cell or jump to next iteration
        animate_cells = show_cell_anim and len(show_cell_anim) > 0

        if current_iteration >= len(bootstrap_engine.iteration_details):
            # We've reached the end
            store_data['is_playing'] = False
            raise PreventUpdate

        iteration_detail = bootstrap_engine.iteration_details[current_iteration]
        n_cells = len(iteration_detail['sampling_details'])

        # Advance frame/iteration (but not if triggered by store update from Run All)
        if ctx.triggered_id != 'iteration-store':
            if ctx.triggered_id == 'step-button' or is_playing:
                if animate_cells:
                    # Advance frame by frame within iteration
                    current_frame += 1
                    if current_frame >= n_cells:
                        # Move to next iteration
                        current_iteration += 1
                        current_frame = 0
                else:
                    # Skip animation, jump to next iteration
                    current_iteration += 1
                    current_frame = n_cells - 1  # Show final state

            # Update store with new values
            store_data['current_iteration'] = current_iteration
            store_data['current_frame'] = current_frame

        # Stop if we've completed all iterations
        if current_iteration >= n_iterations:
            store_data['is_playing'] = False
            current_iteration = n_iterations - 1

        # Get current iteration detail
        iteration_detail = bootstrap_engine.iteration_details[min(current_iteration, len(bootstrap_engine.iteration_details) - 1)]

        # Create visualizations
        if animate_cells and current_frame < len(iteration_detail['sampling_details']):
            # Show animated sampling frame
            main_fig = visualizer.create_sampling_animation_frame(
                iteration_detail,
                current_frame
            )

            # Highlight sampled residual in pool
            current_sample = iteration_detail['sampling_details'][current_frame]
            # Find the index in residual pool
            residual_idx = current_sample.get('sampled_residual_index')

            if residual_idx is None and bootstrap_engine.residual_pool:
                for idx, r in enumerate(bootstrap_engine.residual_pool):
                    if (
                        r.get('origin') == current_sample.get('sampled_from_origin') and
                        r.get('dev') == current_sample.get('sampled_from_dev')
                    ):
                        residual_idx = idx
                        break

            residual_fig = visualizer.create_residual_pool_scatter(
                bootstrap_engine.residual_pool,
                highlighted_idx=residual_idx
            )
        else:
            # Show completed bootstrap triangle
            main_fig = visualizer.create_triangle_heatmap(
                iteration_detail['bootstrap_incremental'],
                f"Bootstrap Triangle - Iteration {current_iteration + 1}",
                colorscale='Purples',
                value_divisor=1000,
                colorbar_title="$000s",
                hover_suffix=" ($000s)"
            )

            residual_fig = visualizer.create_residual_pool_scatter(
                bootstrap_engine.residual_pool
            )

        # Create distribution and statistics
        reserves_so_far = bootstrap_engine.reserve_estimates[:current_iteration + 1]
        current_reserve = iteration_detail['reserve_estimate']

        dist_fig = visualizer.create_reserve_distribution(
            reserves_so_far,
            current_estimate=current_reserve,
            base_reserve=bootstrap_engine._calculate_base_reserve()
        )

        stats_fig = visualizer.create_statistics_panel(
            {'reserve_estimates': reserves_so_far},
            current_iteration
        )

        # Progress text
        if animate_cells and current_frame < n_cells:
            progress_text = f"Iteration {current_iteration + 1}/{n_iterations} - Sampling cell {current_frame + 1}/{n_cells}"
        else:
            progress_text = f"Iteration {current_iteration + 1}/{n_iterations} complete"

        # Statistics text
        if len(reserves_so_far) > 0:
            import numpy as np
            stats_text = (
                f"Mean Reserve: {np.mean(reserves_so_far):,.0f} | "
                f"Std Dev: {np.std(reserves_so_far):,.0f} | "
                f"Current: {current_reserve:,.0f}"
            )
        else:
            stats_text = "No statistics yet"

        return store_data, main_fig, residual_fig, dist_fig, stats_fig, progress_text, stats_text

    @app.callback(
        [
            Output('triangle-mode-store', 'data'),
            Output('btn-cumulative', 'color'),
            Output('btn-incremental', 'color'),
        ],
        [
            Input('btn-cumulative', 'n_clicks'),
            Input('btn-incremental', 'n_clicks'),
        ],
        [State('triangle-mode-store', 'data')],
        prevent_initial_call=True
    )
    def toggle_triangle_mode(cum_clicks, incr_clicks, current_mode):
        """Toggle between cumulative and incremental triangle display."""
        triggered_id = ctx.triggered_id

        if triggered_id == 'btn-cumulative':
            return 'cumulative', 'primary', 'secondary'
        elif triggered_id == 'btn-incremental':
            return 'incremental', 'secondary', 'primary'

        # Default
        return current_mode, 'primary' if current_mode == 'cumulative' else 'secondary', 'primary' if current_mode == 'incremental' else 'secondary'

    @app.callback(
        Output('actual-triangle-graph', 'figure'),
        [Input('triangle-mode-store', 'data')],
        prevent_initial_call=False
    )
    def update_actual_triangle(mode):
        """Update actual triangle display based on mode."""
        if mode == 'cumulative':
            # Get cumulative triangle
            cumulative_data = bootstrap_engine.triangle.values[0, 0]
            fig = visualizer.create_triangle_heatmap(
                cumulative_data,
                "Actual Loss Triangle (Cumulative)",
                colorscale='Greens',
                value_divisor=1000,
                colorbar_title="$000s",
                hover_suffix=" ($000s)"
            )
        else:
            # Get incremental triangle
            incremental_data = bootstrap_engine.actual_incremental.values[0, 0]
            fig = visualizer.create_triangle_heatmap(
                incremental_data,
                "Actual Loss Triangle (Incremental)",
                colorscale='Greens',
                value_divisor=1000,
                colorbar_title="$000s",
                hover_suffix=" ($000s)"
            )

        return fig

    @app.callback(
        [
            Output('original-triangle-graph', 'figure'),
            Output('residual-triangle-graph', 'figure'),
        ],
        [Input('interval-component', 'n_intervals')],
        prevent_initial_call=False
    )
    def update_static_triangles(n):
        """Update static triangle displays (fitted and residuals)."""
        metadata = bootstrap_engine.get_triangle_metadata()

        # Fitted triangle (expected values from model)
        fitted_fig = visualizer.create_triangle_heatmap(
            metadata['fitted_incremental'],
            "Fitted Incremental Triangle (Model Expected Values)",
            colorscale='Blues',
            value_divisor=1000,
            colorbar_title="$000s",
            hover_suffix=" ($000s)"
        )

        # Residual triangle
        residual_fig = visualizer.create_triangle_heatmap(
            metadata['residuals'],
            "Pearson Residuals",
            colorscale='RdBu',
            text_format="{:,.2f}",
            hover_format="{:,.2f}",
            colorbar_title="Residual"
        )

        return fitted_fig, residual_fig

    @app.callback(
        [
            Output('dataset-info', 'children'),
        ],
        [Input('dataset-dropdown', 'value')],
        prevent_initial_call=False
    )
    def update_dataset(dataset_name):
        """Update dataset when dropdown changes."""
        import chainladder as cl
        from dash import html

        # Load the selected dataset
        if dataset_name == 'genins':
            triangle = cl.load_sample('genins')
        elif dataset_name == 'raa':
            triangle = cl.load_sample('raa')
        elif dataset_name == 'abc':
            triangle = cl.load_sample('abc')
        elif dataset_name == 'quarterly':
            triangle = cl.load_sample('quarterly')
        elif dataset_name == 'ukmotor':
            triangle = cl.load_sample('ukmotor')
        elif dataset_name == 'mw2008':
            triangle = cl.load_sample('MW2008')
        elif dataset_name == 'mw2014':
            triangle = cl.load_sample('MW2014')
        else:
            triangle = cl.load_sample('genins')

        # Update the bootstrap engine with new dataset
        bootstrap_engine.__init__(triangle_data=triangle, random_state=42)

        # Get new metadata
        metadata = bootstrap_engine.get_triangle_metadata()

        # Update visualizer metadata
        visualizer.metadata = metadata

        # Return updated info display
        return [html.P([
            html.Strong("Size: "),
            f"{metadata['n_origin']} accident years × {metadata['n_dev']} development periods | ",
            html.Strong("Base Reserve: "),
            f"${metadata['base_reserve']:,.0f}"
        ], className="mb-0", style={'marginTop': '8px'})]

    @app.callback(
        Output('dev-factors-display', 'children'),
        [Input('dataset-dropdown', 'value')],
        prevent_initial_call=False
    )
    def update_dev_factors(dataset_name):
        """Display incremental and cumulative development factors."""
        from dash import html
        import dash_bootstrap_components as dbc
        import numpy as np

        # Get the current triangle's development factors
        model = bootstrap_engine.base_model
        ldf = model.ldf_.values[0, 0, 0, :]
        cdf = model.cdf_.values[0, 0, 0, :]

        # Get development period labels
        n_dev = len(ldf)
        dev_periods = bootstrap_engine.triangle.development.values

        # Create headers for development period pairs
        headers = []
        for i in range(n_dev):
            if i < len(dev_periods) - 1:
                headers.append(f"{dev_periods[i]}-{dev_periods[i+1]}")

        # Build table with both incremental and cumulative LDFs
        table_header = [
            html.Thead(html.Tr([html.Th("Factor Type")] + [html.Th(h, style={'textAlign': 'center'}) for h in headers]))
        ]

        # Incremental LDF row
        incr_cells = [html.Td("Incremental LDF", style={'fontWeight': 'bold'})]
        for i in range(len(headers)):
            incr_cells.append(html.Td(f"{ldf[i]:.4f}", style={'textAlign': 'center'}))

        # Cumulative LDF row
        cum_cells = [html.Td("Cumulative LDF", style={'fontWeight': 'bold'})]
        for i in range(len(headers)):
            cum_cells.append(html.Td(f"{cdf[i]:.4f}", style={'textAlign': 'center'}))

        table_body = [html.Tbody([
            html.Tr(incr_cells),
            html.Tr(cum_cells)
        ])]

        return dbc.Table(table_header + table_body, bordered=True, hover=True, striped=True, size='sm')
