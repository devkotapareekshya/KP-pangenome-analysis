#!/usr/bin/env bash
# Annotates all downloaded genomes with Prokka, then builds the pangenome with Panaroo.
# Also runs Kleborate for K. pneumoniae-specific AMR/virulence/ST scoring.

set -euo pipefail

GENOME_DIR="../../data/genomes"
ANNOT_DIR="../../annotations"
PANGENOME_DIR="../results/panaroo_output"
KLEBORATE_DIR="../results/kleborate_raw"

mkdir -p "$ANNOT_DIR" "$PANGENOME_DIR" "$KLEBORATE_DIR"

# --- 1. Prokka annotation (consistent gene calls across all genomes) ---
for FASTA in "${GENOME_DIR}"/*.fna; do
    ACC=$(basename "$FASTA" .fna)
    echo "Annotating $ACC ..."
    prokka --outdir "${ANNOT_DIR}/${ACC}" --prefix "$ACC" \
        --genus Klebsiella --species pneumoniae --centre X --compliant \
        --cpus 4 --force "$FASTA"
done

# --- 2. Kleborate (AMR + virulence + ST typing, K. pneumoniae-specific) ---
echo "Running Kleborate on all genomes ..."
kleborate -a "${GENOME_DIR}"/*.fna -o "${KLEBORATE_DIR}/kleborate_results.txt" \
    --all

# --- 3. Panaroo (pangenome construction from Prokka GFF3 outputs) ---
echo "Running Panaroo ..."
panaroo -i "${ANNOT_DIR}"/*/*.gff -o "$PANGENOME_DIR" \
    --clean-mode strict --cpus 4

echo "Done. Pangenome summary in ${PANGENOME_DIR}/summary_statistics.txt"
echo "Kleborate results in ${KLEBORATE_DIR}/kleborate_results.txt"

# --- Storage cleanup reminder ---
echo ""
echo "NOTE: Prokka annotation folders and Panaroo intermediate alignment files"
echo "are gitignored. Once you've confirmed results, you can safely delete"
echo "${ANNOT_DIR}/*/ and ${PANGENOME_DIR}/aligned_gene_sequences/ to reclaim disk space,"
echo "since they can be regenerated from data/genomes/ + this script."
