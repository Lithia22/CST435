import json
import matplotlib.pyplot as plt
import numpy as np
import os

def load_results():
    """Load results from both implementations"""
    try:
        with open('results/performance_data/multiprocessing_results.json', 'r') as f:
            mp_results = json.load(f)
    except:
        mp_results = {}
    
    try:
        with open('results/performance_data/futures_results.json', 'r') as f:
            futures_results = json.load(f)
    except:
        futures_results = {}
    
    return mp_results, futures_results

def calculate_speedup(results):
    """Calculate speedup compared to single process/worker"""
    speedups = {}
    
    if not results:
        return speedups
    
    # Handle both string and integer keys
    processes = []
    for k in results.keys():
        try:
            processes.append(int(k))
        except:
            processes.append(k)
    
    processes = sorted(processes)
    
    # Get baseline (single process)
    baseline_key = None
    if 1 in processes:
        baseline_key = 1
    elif '1' in results:
        baseline_key = '1'
    elif 1 in results: 
        baseline_key = 1
    
    if baseline_key is None:
        return speedups
    
    baseline_time = results[baseline_key]['total_time']
    
    for p in processes:
        key_to_use = None
        if p in results:
            key_to_use = p
        elif str(p) in results:
            key_to_use = str(p)
        
        if key_to_use is None:
            continue
            
        if p == 1 or p == '1':
            speedups[p] = 1.0
        else:
            speedups[p] = baseline_time / results[key_to_use]['total_time']
    
    return speedups

def calculate_efficiency(speedups):
    """Calculate efficiency = speedup / number_of_processes"""
    efficiencies = {}
    
    for procs, speedup in speedups.items():
        try:
            procs_num = int(procs) if isinstance(procs, str) else procs
            efficiencies[procs] = speedup / procs_num if procs_num > 0 else 0
        except:
            efficiencies[procs] = 0
    
    return efficiencies

def plot_comparison(mp_results, futures_results):
    """Create comparison plots"""
    if not mp_results and not futures_results:
        print("No results to plot!")
        return
    
    # Calculate speedups and efficiencies
    mp_speedups = calculate_speedup(mp_results)
    futures_speedups = calculate_speedup(futures_results)
    
    if not mp_speedups and not futures_speedups:
        print("No valid data to calculate speedups.")
        return
    
    mp_efficiencies = calculate_efficiency(mp_speedups)
    futures_efficiencies = calculate_efficiency(futures_speedups)
    
    # Get all process counts from both implementations
    all_processes = set()
    for d in [mp_speedups, futures_speedups]:
        all_processes.update(d.keys())
    
    processes = sorted(all_processes)
    
    if not processes:
        print("No process data available for plotting.")
        return
    
    # Prepare data for plotting
    mp_times = []
    futures_times = []
    mp_speedup_vals = []
    futures_speedup_vals = []
    mp_eff_vals = []
    futures_eff_vals = []
    
    for p in processes:
        # Get times
        mp_time = None
        futures_time = None
        
        # Try integer key
        if p in mp_results:
            mp_time = mp_results[p]['total_time']
        elif str(p) in mp_results:
            mp_time = mp_results[str(p)]['total_time']
        
        if p in futures_results:
            futures_time = futures_results[p]['total_time']
        elif str(p) in futures_results:
            futures_time = futures_results[str(p)]['total_time']
        
        mp_times.append(mp_time if mp_time is not None else 0)
        futures_times.append(futures_time if futures_time is not None else 0)
        
        # Get speedups and efficiencies
        mp_speedup_vals.append(mp_speedups.get(p, 0))
        futures_speedup_vals.append(futures_speedups.get(p, 0))
        mp_eff_vals.append(mp_efficiencies.get(p, 0))
        futures_eff_vals.append(futures_efficiencies.get(p, 0))
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Plot 1: Execution Time Comparison
    ax1 = axes[0, 0]
    if any(t > 0 for t in mp_times) or any(t > 0 for t in futures_times):
        x_pos = np.arange(len(processes))
        width = 0.35
        
        bars1 = ax1.bar(x_pos - width/2, mp_times, width, label='Multiprocessing', alpha=0.8, color='blue')
        bars2 = ax1.bar(x_pos + width/2, futures_times, width, label='Concurrent.Futures', alpha=0.8, color='orange')
        
        ax1.set_xlabel('Number of Processes/Workers', fontsize=12)
        ax1.set_ylabel('Execution Time (seconds)', fontsize=12)
        ax1.set_title('Execution Time Comparison', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(processes, fontsize=11)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                            f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    else:
        ax1.text(0.5, 0.5, 'No timing data available', 
                ha='center', va='center', transform=ax1.transAxes, fontsize=12)
        ax1.set_title('Execution Time Comparison', fontsize=14, fontweight='bold')
    
    # Plot 2: Speedup Comparison
    ax2 = axes[0, 1]
    if any(s > 0 for s in mp_speedup_vals) or any(s > 0 for s in futures_speedup_vals):
        ax2.plot(processes, mp_speedup_vals, 'o-', label='Multiprocessing', 
                linewidth=2, markersize=8, color='blue')
        ax2.plot(processes, futures_speedup_vals, 's-', label='Concurrent.Futures', 
                linewidth=2, markersize=8, color='orange')
        ax2.plot(processes, processes, '--', label='Ideal Speedup', 
                alpha=0.5, color='gray', linewidth=2)
        
        ax2.set_xlabel('Number of Processes/Workers', fontsize=12)
        ax2.set_ylabel('Speedup', fontsize=12)
        ax2.set_title('Speedup Comparison', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # Add data point labels
        for i, (mp_val, fut_val) in enumerate(zip(mp_speedup_vals, futures_speedup_vals)):
            if mp_val > 0:
                ax2.text(processes[i], mp_val + 0.05, f'{mp_val:.2f}', 
                        ha='center', va='bottom', fontsize=9)
            if fut_val > 0:
                ax2.text(processes[i], fut_val - 0.1, f'{fut_val:.2f}', 
                        ha='center', va='top', fontsize=9)
    else:
        ax2.text(0.5, 0.5, 'No speedup data available', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Speedup Comparison', fontsize=14, fontweight='bold')
    
    # Plot 3: Efficiency Comparison
    ax3 = axes[1, 0]
    if any(e > 0 for e in mp_eff_vals) or any(e > 0 for e in futures_eff_vals):
        ax3.plot(processes, mp_eff_vals, 'o-', label='Multiprocessing', 
                linewidth=2, markersize=8, color='blue')
        ax3.plot(processes, futures_eff_vals, 's-', label='Concurrent.Futures', 
                linewidth=2, markersize=8, color='orange')
        ax3.axhline(y=1, color='r', linestyle='--', alpha=0.5, label='Ideal Efficiency', linewidth=2)
        
        ax3.set_xlabel('Number of Processes/Workers', fontsize=12)
        ax3.set_ylabel('Efficiency', fontsize=12)
        ax3.set_title('Efficiency Comparison', fontsize=14, fontweight='bold')
        ax3.legend(fontsize=11)
        ax3.grid(True, alpha=0.3, linestyle='--')
        
        # Add data point labels
        for i, (mp_val, fut_val) in enumerate(zip(mp_eff_vals, futures_eff_vals)):
            if mp_val > 0:
                ax3.text(processes[i], mp_val + 0.02, f'{mp_val:.2f}', 
                        ha='center', va='bottom', fontsize=9)
            if fut_val > 0:
                ax3.text(processes[i], fut_val - 0.03, f'{fut_val:.2f}', 
                        ha='center', va='top', fontsize=9)
    else:
        ax3.text(0.5, 0.5, 'No efficiency data available', 
                ha='center', va='center', transform=ax3.transAxes, fontsize=12)
        ax3.set_title('Efficiency Comparison', fontsize=14, fontweight='bold')
    
    # Plot 4: Results Summary Table
    ax4 = axes[1, 1]
    ax4.axis('tight')
    ax4.axis('off')
    
    # Create table data
    table_data = []
    headers = ['Proc', 'MP Time(s)', 'Fut Time(s)', 'MP Speedup', 'Fut Speedup', 'MP Eff', 'Fut Eff']
    
    for i, p in enumerate(processes):
        row = [
            str(p),
            f"{mp_times[i]:.2f}" if mp_times[i] > 0 else "N/A",
            f"{futures_times[i]:.2f}" if futures_times[i] > 0 else "N/A",
            f"{mp_speedup_vals[i]:.2f}" if mp_speedup_vals[i] > 0 else "N/A",
            f"{futures_speedup_vals[i]:.2f}" if futures_speedup_vals[i] > 0 else "N/A",
            f"{mp_eff_vals[i]:.2f}" if mp_eff_vals[i] > 0 else "N/A",
            f"{futures_eff_vals[i]:.2f}" if futures_eff_vals[i] > 0 else "N/A"
        ]
        table_data.append(row)
    
    if table_data:
        table = ax4.table(cellText=table_data, colLabels=headers, 
                         cellLoc='center', loc='center', colWidths=[0.1, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        
        # Style the header row
        for j in range(len(headers)):
            table[(0, j)].set_facecolor('#404040')
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        ax4.set_title('Performance Summary', fontsize=14, fontweight='bold', pad=20)
    else:
        ax4.text(0.5, 0.5, 'No data for summary table', 
                ha='center', va='center', transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Performance Summary', fontsize=14, fontweight='bold')
    
    plt.suptitle('Parallel Image Processing Performance Analysis', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    plt.savefig('results/performance_comparison.png', dpi=300, bbox_inches='tight')
    
    print("Performance graph saved as: results/performance_comparison.png")
    
    # Show the plot
    plt.show()
    
    # Print analysis
    print("\nPERFORMANCE ANALYSIS SUMMARY")
    print("="*50)
    
    print("\nSPEEDUP ANALYSIS:")
    print(f"{'Processes':<10} {'MP Time':<12} {'MP Speedup':<12} {'Fut Time':<12} {'Fut Speedup':<12}")
    for i, p in enumerate(processes):
        print(f"{p:<10} {mp_times[i]:<12.2f} {mp_speedup_vals[i]:<12.2f} "
              f"{futures_times[i]:<12.2f} {futures_speedup_vals[i]:<12.2f}")
    
    print("\nEFFICIENCY ANALYSIS:")
    print(f"{'Processes':<10} {'MP Efficiency':<15} {'Fut Efficiency':<15}")
    for i, p in enumerate(processes):
        print(f"{p:<10} {mp_eff_vals[i]:<15.2f} {futures_eff_vals[i]:<15.2f}")
        
if __name__ == "__main__":
    mp_results, futures_results = load_results()
    plot_comparison(mp_results, futures_results)