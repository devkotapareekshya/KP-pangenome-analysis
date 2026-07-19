import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# Load presence/absence matrix
df = pd.read_csv("pangenome/results/panaroo/gene_presence_absence.csv", low_memory=False)

# Get sample columns (exclude Gene, Non-unique Gene name, Annotation)
sample_cols = [c for c in df.columns if c not in ["Gene", "Non-unique Gene name", "Annotation"]]

# Convert to binary
pa = df[sample_cols].copy()
for col in sample_cols:
    pa[col] = pa[col].notna() & (pa[col] != "")

# Accumulation curve — random permutations
n_permutations = 20
n_samples = len(sample_cols)
total_curves = []
core_curves = []

random.seed(42)
for _ in range(n_permutations):
    order = random.sample(sample_cols, n_samples)
    total = []
    core = []
    for i in range(1, n_samples + 1):
        subset = pa[order[:i]]
        total.append((subset.sum(axis=1) > 0).sum())
        core.append((subset.sum(axis=1) == i).sum())
    total_curves.append(total)
    core_curves.append(core)

total_arr = np.array(total_curves)
core_arr  = np.array(core_curves)

x = range(1, n_samples + 1)

fig, ax = plt.subplots(figsize=(9, 6))

# Plot all permutations faintly
for curve in total_curves:
    ax.plot(x, curve, color="#EF5350", alpha=0.15, linewidth=0.8)
for curve in core_curves:
    ax.plot(x, curve, color="#42A5F5", alpha=0.15, linewidth=0.8)

# Plot means
ax.plot(x, total_arr.mean(axis=0), color="#EF5350", linewidth=2.5,
        label=f"Pan-genome (total: {int(total_arr.mean(axis=0)[-1])} genes)")
ax.plot(x, core_arr.mean(axis=0),  color="#42A5F5", linewidth=2.5,
        label=f"Core genome (final: {int(core_arr.mean(axis=0)[-1])} genes)")

ax.set_xlabel("Number of genomes", fontsize=12)
ax.set_ylabel("Number of genes", fontsize=12)
ax.set_title("K. pneumoniae Pangenome Accumulation Curve\n(n=30: 15 ST258 + 15 ST23)",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.set_xlim(1, n_samples)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("results/figures/accumulation_curve.png", dpi=150, bbox_inches="tight")
print("Saved to results/figures/accumulation_curve.png")
