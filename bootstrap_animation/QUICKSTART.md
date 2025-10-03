# Quick Start Guide

## Installation Complete! ✓

Your virtual environment has been created and all dependencies have been installed.

## Running the Application

### Easiest Way - Use the Script

```bash
./run.sh
```

This script automatically:
- Activates the virtual environment
- Installs any missing dependencies
- Starts the web server

Then open your browser to: **http://127.0.0.1:8050**

### Manual Way

```bash
source venv/bin/activate
python app.py
```

## Using the Application

1. **Set Parameters**
   - Use the **"Number of Bootstrap Iterations"** slider (10-1000)
   - Adjust **"Animation Speed"** slider (0.1× to 10×)
   - Check/uncheck **"Show cell-by-cell sampling animation"**

2. **Start Animation**
   - Click the green **"Play"** button
   - First time: application will compute all bootstrap iterations (~5-10 seconds for 100 iterations)
   - Animation will begin automatically

3. **Control Playback**
   - **Pause**: Click the button again to pause
   - **Step**: Advance one frame at a time
   - **Reset**: Start over from the beginning

4. **View Results**
   - **Main Triangle**: See bootstrap triangle being built cell-by-cell
   - **Residual Pool**: Scatter plot of available residuals (highlighted when sampled)
   - **Reserve Distribution**: Histogram building in real-time
   - **Convergence Plot**: Track how estimates stabilize over iterations

5. **Additional Info**
   - Expand **"View Original Triangle & Residuals"** at the bottom
   - See the source data and calculated Pearson residuals

## What You're Seeing

### The Animation Process

Each iteration:
1. Samples a residual from the pool (with replacement)
2. Applies it to the fitted value: `fitted + residual × √fitted`
3. Builds a new bootstrap triangle
4. Projects reserves using chain ladder method
5. Adds estimate to the distribution

### Interpreting Results

- **Mean Reserve**: Average across all bootstrap iterations
- **Distribution Shape**: Shows uncertainty in reserve estimate
- **Convergence**: More iterations = smoother, more stable distribution
- **Base Reserve**: Green line = deterministic chain ladder estimate

## Tips for Best Experience

### For Learning
- Start with **10-50 iterations**, **1× speed**, **cell animation ON**
- Watch individual residuals being sampled
- Observe how different residuals affect the result

### For Quick Results
- Use **100-1000 iterations**, **5-10× speed**, **cell animation OFF**
- Skip to see final distributions quickly
- Better statistical convergence

### Performance Notes
- **First Play**: Computes all iterations (may take a few seconds)
- **Subsequent Plays**: Uses cached results (instant)
- **Reset**: Clears cache, requires re-computation
- **High Iterations** (1000+): Longer initial computation, but smooth animation

## Troubleshooting

### "Application failed to start"
```bash
cd bootstrap_animation
source venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

### "Module not found" errors
Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

### Port already in use
Change port in `app.py` (last line):
```python
app.run_server(debug=True, host='127.0.0.1', port=8051)  # Changed to 8051
```

### Animation is laggy
- Reduce number of iterations
- Turn off cell-by-cell animation
- Increase animation speed (reduces frame rate)

## Customization

### Use Your Own Data

Edit `bootstrap_engine.py`, replace:
```python
self.triangle = cl.load_sample('genins')
```

With your own triangle:
```python
import pandas as pd
df = pd.read_csv('your_data.csv')
self.triangle = cl.Triangle(df, origin='origin_col', development='dev_col', columns='value_col')
```

### Change Sample Data

Available samples in chainladder:
- `'genins'` - GenIns (default)
- `'raa'` - RAA
- `'abc'` - ABC
- `'quarterly'` - Quarterly data
- `'ukmotor'` - UK Motor

Replace in `bootstrap_engine.py`:
```python
self.triangle = cl.load_sample('raa')  # Use RAA instead
```

## Next Steps

- **Experiment**: Try different iteration counts and speeds
- **Learn**: Read `README.md` for methodology details
- **Explore**: Check `IMPLEMENTATION.md` for technical details
- **Customize**: Modify the code to fit your needs

## Support

For issues or questions:
- Check `README.md` for detailed documentation
- Review `test_bootstrap.py` for usage examples
- Examine source code - it's well-commented!

---

**Enjoy exploring the Shapland ODP Bootstrap methodology!** 🎉
