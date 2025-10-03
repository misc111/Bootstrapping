# Bootstrap Animation - Shapland ODP Method

Interactive visualization and animation of Mark R. Shapland's Over-Dispersed Poisson (ODP) Bootstrap methodology for actuarial loss reserving.

## About

This application implements the bootstrap methodology described in **"Using the ODP Bootstrap Model: A Practitioner's Guide"** by Mark R. Shapland (CAS Monograph No. 4, 2016). It provides a beautiful, animated visualization of the residual sampling process that forms the core of the ODP bootstrap technique.

## Features

- **Real-time Animation**: Watch each residual being sampled cell-by-cell during bootstrap iterations
- **Interactive Controls**:
  - Adjust number of iterations (10-1,000)
  - Control animation speed (0.1× to 10×)
  - Toggle cell-by-cell animation on/off
  - Play/Pause/Step through iterations
- **Beautiful Visualizations**:
  - Bootstrap triangle heatmap with sampling animation
  - Residual pool scatter plot
  - Reserve distribution histogram
  - Convergence statistics
- **Educational**: Perfect for understanding the bootstrap sampling process

## Installation & Usage

### Setup (One Time)

1. Create virtual environment:
```bash
python3 -m venv venv
```

2. Activate it:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Run the Application

```bash
source venv/bin/activate  # Activate venv
python app.py
```

Then open your browser to: **http://127.0.0.1:8050**

**Quick start script (does everything):**
```bash
./run.sh
```

## Testing

**Verify everything works before running:**

```bash
./run_tests.sh
```

This runs a comprehensive test suite (22 tests) that checks:
- All dependencies are installed
- All modules import correctly
- Core functionality works
- Visualizations render properly

See **TEST_GUIDE.md** for detailed testing documentation.

### How to Use

1. **Set Parameters**:
   - Choose the number of bootstrap iterations (more iterations = better distribution estimate)
   - Adjust animation speed based on your preference

2. **Start Animation**:
   - Click "Play" to start the bootstrap simulation
   - The first time you click Play, all iterations are computed (may take a few seconds)
   - Animation will show each residual being sampled

3. **Interactive Features**:
   - Use "Step" to advance frame-by-frame
   - Toggle cell-by-cell animation for faster iteration completion
   - Click "Reset" to start over with new parameters

4. **View Results**:
   - Watch the reserve distribution build up in real-time
   - Monitor convergence statistics
   - Expand "View Original Triangle & Residuals" to see source data

## Methodology

### The ODP Bootstrap Process

1. **Fit Base Model**: Chain ladder model is fit to original triangle
2. **Calculate Residuals**: Pearson residuals = (Actual - Fitted) / √Fitted
3. **Adjust Residuals**: Apply degrees of freedom adjustment
4. **Sample with Replacement**: Randomly select residuals from the pool
5. **Generate Bootstrap Triangle**: Fitted + Sampled Residual × √Fitted
6. **Project Reserves**: Apply chain ladder to bootstrap triangle
7. **Repeat**: Steps 4-6 for N iterations
8. **Analyze Distribution**: Study the distribution of reserve estimates

### Key Formulas

**Unscaled Pearson Residuals:**
```
r(w,d) = [q(w,d) - m(w,d)] / sqrt(m(w,d))
```

**Adjusted Residuals:**
```
r_adj = sqrt(n / DF) × r
```

**Bootstrap Sample:**
```
q*(w,d) = m(w,d) + r* × sqrt(m(w,d))
```

Where:
- `q(w,d)` = actual incremental loss
- `m(w,d)` = fitted incremental loss
- `n` = number of data points
- `DF` = degrees of freedom
- `r*` = sampled adjusted residual

## Project Structure

```
bootstrap_animation/
├── app.py                 # Main Dash application
├── bootstrap_engine.py    # ODP bootstrap implementation
├── visualization.py       # Plotly visualization functions
├── callbacks.py          # Dash callback handlers
├── requirements.txt      # Python dependencies
├── assets/
│   └── styles.css       # Custom CSS styling
└── README.md            # This file
```

## Technical Details

- **Framework**: Plotly Dash (Python web framework)
- **Visualization**: Plotly (interactive graphing library)
- **Actuarial Engine**: chainladder-python (loss reserving library)
- **Styling**: Bootstrap 5 + custom CSS

## References

- Shapland, M. R. (2016). *Using the ODP Bootstrap Model: A Practitioner's Guide*. CAS Monograph Series No. 4.
- England, P. D., & Verrall, R. J. (2002). Stochastic claims reserving in general insurance. *British Actuarial Journal*, 8(3), 443-518.

## License

Educational and research use.

## Author

Implementation based on the research and methodology of Mark R. Shapland, FCAS.
