#! /bin/bash

set -eo pipefail

SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. ~/python3_venv/bin/activate

dosage_in_month()
{
    local year="$1"
    local month="$2"
    python3 "$SCRIPTDIR"/dosage_by_month.py "$year" "$month"
}

year=1999
for month in {8..12}
do
    dosage_in_month $year $month
done

for year in {2000..2025}
do
    for month in {1..12}
    do
	dosage_in_month $year $month
    done
done

year=2026
for month in {1..6}
do
    dosage_in_month $year $month
done

deactivate
