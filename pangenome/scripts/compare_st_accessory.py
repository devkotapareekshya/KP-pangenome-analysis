import pandas as pd

# Load presence/absence matrix
df = pd.read_csv("pangenome/results/panaroo/gene_presence_absence.csv", low_memory=False)

# Identify ST258 and ST23 columns
st258_cols = [c for c in df.columns if "ST258" in c]
st23_cols = [c for c in df.columns if "ST23" in c]

print(f"ST258 genomes: {len(st258_cols)}")
print(f"ST23 genomes:  {len(st23_cols)}")

# Convert to binary presence/absence
pa = df.copy()
for col in st258_cols + st23_cols:
    pa[col] = pa[col].notna() & (pa[col] != "")

# Calculate presence frequency per ST
pa["st258_freq"] = pa[st258_cols].sum(axis=1) / len(st258_cols)
pa["st23_freq"]  = pa[st23_cols].sum(axis=1)  / len(st23_cols)

# Classify genes
def classify(row):
    if row["st258_freq"] >= 0.99 and row["st23_freq"] >= 0.99:
        return "core_both"
    elif row["st258_freq"] >= 0.8 and row["st23_freq"] <= 0.2:
        return "ST258_enriched"
    elif row["st23_freq"] >= 0.8 and row["st258_freq"] <= 0.2:
        return "ST23_enriched"
    else:
        return "other"

pa["category"] = pa.apply(classify, axis=1)

# Summary
print("\n=== GENE CATEGORY SUMMARY ===")
print(pa["category"].value_counts())

# ST258-enriched genes
print("\n=== TOP ST258-ENRICHED GENES ===")
st258_enriched = pa[pa["category"] == "ST258_enriched"][["Gene", "Annotation", "st258_freq", "st23_freq"]]
print(st258_enriched.head(20).to_string(index=False))

# ST23-enriched genes
print("\n=== TOP ST23-ENRICHED GENES ===")
st23_enriched = pa[pa["category"] == "ST23_enriched"][["Gene", "Annotation", "st258_freq", "st23_freq"]]
print(st23_enriched.head(20).to_string(index=False))

# Save results
st258_enriched.to_csv("pangenome/results/ST258_enriched_genes.csv", index=False)
st23_enriched.to_csv("pangenome/results/ST23_enriched_genes.csv", index=False)
print("\nSaved results to pangenome/results/")
