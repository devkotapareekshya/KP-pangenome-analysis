#!/usr/bin/env bash

ACCESSION_LIST="data/all_kp_refseq_complete.txt"
GENOME_DIR="data/genomes/confirmed"
TEMP_DIR="data/genomes/tmp_batch"
KLEBORATE_DIR="pangenome/results/kleborate"
TARGET_ST258=15
TARGET_ST23=15
BATCH_SIZE=20
OFFSET=0
BATCH_NUM=0

mkdir -p "$GENOME_DIR" "$TEMP_DIR" "$KLEBORATE_DIR"

count_st() {
    ls "${GENOME_DIR}"/*_${1}.fna 2>/dev/null | wc -l
}

mapfile -t ALL_ACCS < <(awk 'NR>1 {print $1}' "$ACCESSION_LIST")
TOTAL=${#ALL_ACCS[@]}
echo "Total accessions available: $TOTAL"

while true; do
    HAVE_ST258=$(count_st ST258)
    HAVE_ST23=$(count_st ST23)
    echo "Progress: ST258=${HAVE_ST258}/${TARGET_ST258}, ST23=${HAVE_ST23}/${TARGET_ST23}"

    if [ "$HAVE_ST258" -ge "$TARGET_ST258" ] && [ "$HAVE_ST23" -ge "$TARGET_ST23" ]; then
        echo "Done! Target reached."
        break
    fi

    if [ "$OFFSET" -ge "$TOTAL" ]; then
        echo "Exhausted all accessions."
        break
    fi

    BATCH=("${ALL_ACCS[@]:$OFFSET:$BATCH_SIZE}")
    OFFSET=$((OFFSET + BATCH_SIZE))
    BATCH_NUM=$((BATCH_NUM + 1))
    echo "--- Batch ${BATCH_NUM} (offset $OFFSET) ---"

    rm -f "${TEMP_DIR}"/*.fna 2>/dev/null || true

    for ACC in "${BATCH[@]}"; do
        [ -z "$ACC" ] && continue
        echo "  Downloading $ACC..."
        datasets download genome accession "$ACC" \
            --include genome \
            --filename "${TEMP_DIR}/${ACC}.zip" 2>/dev/null || continue
        unzip -o "${TEMP_DIR}/${ACC}.zip" \
            -d "${TEMP_DIR}/${ACC}_tmp" > /dev/null 2>&1 || continue
        find "${TEMP_DIR}/${ACC}_tmp" -name "*.fna" \
            -exec mv {} "${TEMP_DIR}/${ACC}.fna" \; 2>/dev/null || true
        rm -rf "${TEMP_DIR}/${ACC}_tmp" "${TEMP_DIR}/${ACC}.zip"
    done

    FNA_COUNT=$(ls "${TEMP_DIR}"/*.fna 2>/dev/null | wc -l)
    if [ "$FNA_COUNT" -eq 0 ]; then
        echo "  No genomes downloaded, skipping."
        continue
    fi

    echo "  Running Kleborate on $FNA_COUNT genomes..."
    kleborate -a "${TEMP_DIR}"/*.fna \
        -o "${KLEBORATE_DIR}/batch_${BATCH_NUM}" \
        -p kpsc 2>/dev/null || continue

    RESULTS="${KLEBORATE_DIR}/batch_${BATCH_NUM}/kleborate_results.txt"
    [ ! -f "$RESULTS" ] && continue

    while IFS=$'\t' read -r STRAIN SPECIES N50 ST REST; do
        [ "$STRAIN" = "strain" ] && continue
        FNA="${TEMP_DIR}/${STRAIN}.fna"
        [ ! -f "$FNA" ] && continue
        if [ "$ST" = "ST258" ] && [ "$(count_st ST258)" -lt "$TARGET_ST258" ]; then
            echo "  KEEP $STRAIN as ST258"
            cp "$FNA" "${GENOME_DIR}/${STRAIN}_ST258.fna"
        elif [ "$ST" = "ST23" ] && [ "$(count_st ST23)" -lt "$TARGET_ST23" ]; then
            echo "  KEEP $STRAIN as ST23"
            cp "$FNA" "${GENOME_DIR}/${STRAIN}_ST23.fna"
        else
            echo "  SKIP $STRAIN ($ST)"
        fi
    done < "$RESULTS"

done

echo ""
echo "=== FINAL COLLECTION ==="
echo "ST258: $(count_st ST258)"
echo "ST23:  $(count_st ST23)"
du -sh "$GENOME_DIR"
rm -rf "$TEMP_DIR"
