#!/usr/bin/env bash
# Downloads genome ASSEMBLIES ONLY (not raw reads) for accessions listed in
# data/kp_accessions.txt, using the NCBI datasets CLI. Keeps storage light:
# each assembly is ~5-6 MB, so ~30 genomes total should stay well under 250 MB.

set -euo pipefail

ACCESSION_LIST="../../data/kp_accessions.txt"
OUTDIR="../../data/genomes"
mkdir -p "$OUTDIR"

# Strip comments/blank lines from accession list
grep -v '^#' "$ACCESSION_LIST" | grep -v '^\s*$' > /tmp/kp_accessions_clean.txt

while read -r ACC; do
    echo "Downloading $ACC ..."
    datasets download genome accession "$ACC" \
        --include genome \
        --filename "${OUTDIR}/${ACC}.zip"

    # Unzip just the genomic FASTA, discard the rest (README, metadata JSON, etc.)
    unzip -o "${OUTDIR}/${ACC}.zip" -d "${OUTDIR}/${ACC}_tmp" > /dev/null
    find "${OUTDIR}/${ACC}_tmp" -name "*.fna" -exec mv {} "${OUTDIR}/${ACC}.fna" \;
    rm -rf "${OUTDIR}/${ACC}_tmp" "${OUTDIR}/${ACC}.zip"
done < /tmp/kp_accessions_clean.txt

echo "Done. Genome assemblies in ${OUTDIR}/"
du -sh "$OUTDIR"
