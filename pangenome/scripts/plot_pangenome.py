import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# --- Figure 1: Pangenome pie chart ---
categories = ["Core\n(3,977)", "Soft core\n(331)", "Shell\n(1,947)", "Cloud\n(2,435)"]
sizes = [3977, 331, 1947, 2435]
colors = ["#2196F3", "#64B5F6", "#FFA726", "#EF5350"]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].pie(sizes, labels=categories, colors=colors, autopct="%1.1f%%",
            startangle=90, pctdistance=0.75)
axes[0].set_title("K. pneumoniae Pangenome Structure\n(n=30: 15 ST258 + 15 ST23)",
                  fontsize=13, fontweight="bold")

# --- Figure 2: ST258 vs ST23 accessory gene frequency scatter ---
df = pd.read_csv("pangenome/results/panaroo/gene_presence_absence.csv", low_memory=False)
st258_cols = [c for c in df.columns if "ST258" in c]
st23_cols  = [c for c in df.columns if "ST23" in c]

pa = df.copy()
for col in st258_cols + st23_cols:
    pa[col] = pa[col].notna() & (pa[col] != "")

pa["st258_freq"] = pa[st258_cols].sum(axis=1) / len(st258_cols)
pa["st23_freq"]  = pa[st23_cols].sum(axis=1)  / len(st23_cols)

def classify(row):
    if row["st258_freq"] >= 0.99 and row["st23_freq"] >= 0.99:
        return "Core (both)"
    elif row["st258_freq"] >= 0.8 and row["st23_freq"] <= 0.2:
        return "ST258-enriched"
    elif row["st23_freq"] >= 0.8 and row["st258_freq"] <= 0.2:
        return "ST23-enriched"
    else:
        return "Other"

pa["category"] = pa.apply(classify, axis=1)

color_map = {
    "Core (both)": "#90A4AE",
    "ST258-enriched": "#EF5350",
    "ST23-enriched": "#42A5F5",
    "Other": "#CFD8DC"
}

for cat, grp in pa.groupby("category"):
    axes[1].scatter(grp["st258_freq"], grp["st23_freq"],
                    c=color_map[cat], label=cat, alpha=0.6, s=15, edgecolors="none")

axes[1].set_xlabel("Frequency in ST258", fontsize=12)
axes[1].set_ylabel("Frequency in ST23", fontsize=12)
axes[1].set_title("Accessory Gene Frequency:\nST258 vs ST23", fontsize=13, fontweight="bold")
axes[1].legend(loc="upper left", fontsize=9)
axes[1].set_xlim(-0.05, 1.05)
axes[1].set_ylim(-0.05, 1.05)

# Annotate key genes
key_genes = {
    "intA": "ST258-enriched\n(prophage)",
    "algC": "ST23-enriched\n(capsule)",
    "manC1": "ST23-enriched\n(capsule)",
}
for gene, label in key_genes.items():
    row = pa[pa["Gene"].str.contains(gene, na=False)]
    if not row.empty:
        x, y = row.iloc[0]["st258_freq"], row.iloc[0]["st23_freq"]
        axes[1].annotate(gene, (x, y), fontsize=7,
                         xytext=(x+0.05, y+0.05),
                         arrowprops=dict(arrowstyle="-", color="gray", lw=0.8))

plt.tight_layout()
plt.savefig("results/figures/pangenome_comparison.png", dpi=150, bbox_inches="tight")
print("Figure saved to results/figures/pangenome_comparison.png")
