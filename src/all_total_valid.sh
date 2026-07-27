#! /bin/bash

set -eo pipefail
SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. ~/python3_venv/bin/activate

year=1999
for month in {8..12}
do
    python3 "$SCRIPTDIR"/total_valid_shield_dosage.py $year $month
done

for year in {2000..2025}
do
    for month in {1..12}
    do
	python3 "$SCRIPTDIR"/total_valid_shield_dosage.py $year $month
    done
done

year=2026
for month in {1..6}
do
    python3 "$SCRIPTDIR"/total_valid_shield_dosage.py $year $month
done

deactivate
