#! /bin/bash

set -eo pipefail

SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPTDIR"

. ~/python3_venv/bin/activate

obsids_in_month()
{
    local year="$1"
    local month="$2"
    python3 -c '
import HRCDose, sys;
year = int(sys.argv[1])
month = int(sys.argv[2])
obsids = [f"{o:05d}" for o in HRCDose.year_month_obsids_archive(year, month)]
print(f"{year}\t{month}\t{'\',\''.join(obsids)}")
' $year $month
}

year=1999
for month in {8..12}
do
    obsids_in_month $year $month
done

for year in {2000..2025}
do
    for month in {1..12}
    do
	obsids_in_month $year $month
    done
done

year=2026
for month in {1..6}
do
    obsids_in_month $year $month
done

deactivate
cd -
