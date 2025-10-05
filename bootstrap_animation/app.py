"""
Main Dash Application for Bootstrap Animation
Animated visualization of Shapland's ODP Bootstrap Methodology
"""

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from bootstrap_engine import AnimatedBootstrapODP
from visualization import BootstrapVisualizer
from callbacks import register_callbacks


# Initialize the bootstrap engine with sample data
print("Initializing bootstrap engine...")
bootstrap_engine = AnimatedBootstrapODP(random_state=42)
metadata = bootstrap_engine.get_triangle_metadata()
print(f"Triangle loaded: {metadata['n_origin']} origins × {metadata['n_dev']} development periods")
print(f"Base reserve estimate: ${metadata['base_reserve']:,.0f}")

# Initialize visualizer
visualizer = BootstrapVisualizer(metadata)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "Bootstrap Animation - Shapland ODP Method"

# Define layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Shapland ODP Bootstrap Methodology", className="text-center mb-2"),
            html.H5(
                "Interactive Animation of Residual Sampling Process",
                className="text-center text-muted mb-4"
            ),
        ])
    ]),

    # Dataset Selection and Information Panel
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Dataset:", className="mb-1"),
                            dcc.Dropdown(
                                id='dataset-dropdown',
                                options=[
                                    {'label': 'GenIns (General Insurance)', 'value': 'genins'},
                                    {'label': 'RAA (Reinsurance Association of America)', 'value': 'raa'},
                                    {'label': 'ABC', 'value': 'abc'},
                                    {'label': 'Quarterly', 'value': 'quarterly'},
                                    {'label': 'UK Motor', 'value': 'ukmotor'},
                                    {'label': 'MW2008 (Medicare)', 'value': 'mw2008'},
                                    {'label': 'MW2014 (Medicare)', 'value': 'mw2014'},
                                ],
                                value='genins',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Div(id='dataset-info', children=[
                                html.P([
                                    html.Strong("Size: "),
                                    f"{metadata['n_origin']} accident years × {metadata['n_dev']} development periods | ",
                                    html.Strong("Base Reserve: "),
                                    f"${metadata['base_reserve']:,.0f}"
                                ], className="mb-0", style={'marginTop': '8px'})
                            ])
                        ], width=9)
                    ])
                ])
            ], color="light")
        ])
    ], className="mb-3"),

    # Control Panel
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Animation Controls", className="mb-0")),
                dbc.CardBody([
                    # Number of iterations slider
                    html.Label("Number of Bootstrap Iterations:"),
                    dcc.Slider(
                        id='n-iterations-slider',
                        min=10,
                        max=1000,
                        step=10,
                        value=100,
                        marks={
                            10: '10',
                            100: '100',
                            250: '250',
                            500: '500',
                            1000: '1000'
                        },
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Br(),

                    # Animation speed slider
                    html.Label("Animation Speed:"),
                    dcc.Slider(
                        id='speed-slider',
                        min=0.1,
                        max=10,
                        step=0.1,
                        value=1.0,
                        marks={
                            0.1: '0.1×',
                            1: '1×',
                            5: '5×',
                            10: '10×'
                        },
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Br(),

                    # Show cell-by-cell animation checkbox
                    dcc.Checklist(
                        id='show-cell-animation',
                        options=[
                            {'label': ' Show cell-by-cell sampling animation', 'value': 'show'}
                        ],
                        value=['show'],
                        inline=True
                    ),
                    html.Br(),

                    # Control buttons
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Play",
                                id='play-button',
                                color="success",
                                className="me-2",
                                size="lg"
                            ),
                            dbc.Button(
                                "Step",
                                id='step-button',
                                color="primary",
                                className="me-2",
                                size="lg"
                            ),
                            dbc.Button(
                                "Reset",
                                id='reset-button',
                                color="danger",
                                className="me-2",
                                size="lg"
                            ),
                            dbc.Button(
                                "Run All",
                                id='run-all-button',
                                color="info",
                                size="lg"
                            ),
                        ])
                    ]),
                ])
            ])
        ])
    ], className="mb-3"),

    # Progress indicator
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(id='progress-text', children="Ready to start", className="mb-1"),
                    html.P(id='stats-text', children="", className="mb-0 text-muted")
                ])
            ], color="info", outline=True)
        ])
    ], className="mb-3"),

    # Main visualization area
    dbc.Row([
        # Left column: Main triangle and residual pool
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H6([
                    "Bootstrap Triangle (Sampling Animation): ",
                    html.I("q*(w,d) = m(w,d) + sqrt(m(w,d)) × r*")
                ], className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='main-triangle-graph', config={'displayModeBar': False})
                ])
            ], className="mb-3"),

            dbc.Card([
                dbc.CardHeader(html.H6("Residual Pool", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='residual-pool-graph', config={'displayModeBar': False})
                ])
            ])
        ], width=6),

        # Right column: Distribution and statistics
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H6("Reserve Distribution", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='distribution-graph', config={'displayModeBar': False})
                ])
            ], className="mb-3"),

            dbc.Card([
                dbc.CardHeader(html.H6("Reserve Convergence", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='statistics-graph', config={'displayModeBar': False})
                ])
            ])
        ], width=6)
    ], className="mb-3"),

    # Actual Data Triangle Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.H6("Actual Loss Triangle", className="mb-0 d-inline"),
                        html.Div([
                            dbc.ButtonGroup([
                                dbc.Button("Cumulative", id='btn-cumulative', color="primary", size="sm", className="me-1"),
                                dbc.Button("Incremental", id='btn-incremental', color="secondary", size="sm")
                            ], size="sm", className="float-end")
                        ], className="d-inline float-end")
                    ], className="d-flex justify-content-between align-items-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='actual-triangle-graph', config={'displayModeBar': False})
                ])
            ])
        ])
    ], className="mb-3"),

    # Development Factors Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H6("Development Factors", className="mb-0")),
                dbc.CardBody([
                    html.Div(id='dev-factors-display')
                ])
            ])
        ])
    ], className="mb-3"),

    # Reference triangles (collapsible)
    dbc.Row([
        dbc.Col([
            dbc.Accordion([
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='original-triangle-graph', config={'displayModeBar': False})
                        ], width=6),
                        dbc.Col([
                            dcc.Graph(id='residual-triangle-graph', config={'displayModeBar': False})
                        ], width=6)
                    ])
                ], title="View Fitted Values & Residuals")
            ])
        ])
    ], className="mb-3"),

    # Store for triangle display mode
    dcc.Store(id='triangle-mode-store', data='cumulative'),

    # Hidden components for state management
    dcc.Store(id='iteration-store', data={
        'is_playing': False,
        'current_iteration': 0,
        'current_frame': 0,
        'n_iterations': 100,
        'bootstrap_complete': False
    }),

    dcc.Interval(
        id='interval-component',
        interval=100,  # milliseconds
        n_intervals=0,
        disabled=True
    ),

    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                "Implementation of ",
                html.Em("Using the ODP Bootstrap Model: A Practitioner's Guide"),
                " by Mark R. Shapland (CAS Monograph No. 4, 2016)"
            ], className="text-center text-muted small")
        ])
    ])

], fluid=True, className="py-4")


# Register callbacks
register_callbacks(app, bootstrap_engine, visualizer)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Bootstrap Animation Application")
    print("="*60)
    print("\nOpen your browser and navigate to: http://127.0.0.1:8050")
    print("\nInstructions:")
    print("1. Set the number of bootstrap iterations (10-1000)")
    print("2. Adjust animation speed (0.1x to 10x)")
    print("3. Toggle cell-by-cell animation on/off")
    print("4. Click 'Play' to start the animation")
    print("5. Use 'Step' to advance frame-by-frame")
    print("6. Click 'Reset' to start over")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")

    app.run(debug=True, host='127.0.0.1', port=8050)
