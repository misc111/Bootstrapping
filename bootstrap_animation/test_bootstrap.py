"""
Quick test script to validate bootstrap engine functionality
"""

from bootstrap_engine import AnimatedBootstrapODP
from visualization import BootstrapVisualizer

print("="*60)
print("Testing Bootstrap Engine")
print("="*60)

# Test 1: Initialize engine
print("\n1. Initializing bootstrap engine...")
try:
    engine = AnimatedBootstrapODP(random_state=42)
    print("   ✓ Engine initialized successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 2: Get metadata
print("\n2. Getting triangle metadata...")
try:
    metadata = engine.get_triangle_metadata()
    print(f"   ✓ Triangle size: {metadata['n_origin']} × {metadata['n_dev']}")
    print(f"   ✓ Base reserve: ${metadata['base_reserve']:,.2f}")
    print(f"   ✓ Residual pool size: {len(metadata['residual_pool'])}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 3: Run single iteration
print("\n3. Running single bootstrap iteration...")
try:
    result = engine.run_single_iteration(0)
    print(f"   ✓ Iteration completed")
    print(f"   ✓ Reserve estimate: ${result['reserve_estimate']:,.2f}")
    print(f"   ✓ Sampling details: {len(result['sampling_details'])} cells sampled")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 4: Run multiple iterations
print("\n4. Running 10 bootstrap iterations...")
try:
    summary = engine.run_bootstrap(n_iterations=10)
    print(f"   ✓ {summary['n_iterations']} iterations completed")
    print(f"   ✓ Mean reserve: ${summary['mean']:,.2f}")
    print(f"   ✓ Std deviation: ${summary['std']:,.2f}")
    print(f"   ✓ 95th percentile: ${summary['percentiles']['95']:,.2f}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 5: Initialize visualizer
print("\n5. Testing visualizer...")
try:
    visualizer = BootstrapVisualizer(metadata)
    print("   ✓ Visualizer initialized successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 6: Create visualizations
print("\n6. Creating test visualizations...")
try:
    # Triangle heatmap
    fig1 = visualizer.create_triangle_heatmap(
        metadata['actual_incremental'],
        "Test Triangle"
    )
    print("   ✓ Triangle heatmap created")

    # Residual pool
    fig2 = visualizer.create_residual_pool_scatter(metadata['residual_pool'])
    print("   ✓ Residual pool scatter created")

    # Distribution
    fig3 = visualizer.create_reserve_distribution(
        engine.reserve_estimates,
        base_reserve=metadata['base_reserve']
    )
    print("   ✓ Reserve distribution created")

    # Animation frame
    fig4 = visualizer.create_sampling_animation_frame(
        engine.iteration_details[0],
        frame_idx=0
    )
    print("   ✓ Animation frame created")

except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("\n" + "="*60)
print("All tests passed! ✓")
print("="*60)
print("\nYou can now run the full application with:")
print("  python3 app.py")
print("\nThen open your browser to: http://127.0.0.1:8050")
print("="*60)
