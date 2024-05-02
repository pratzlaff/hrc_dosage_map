#! /bin/bash

[ $# -eq 2 ] || {
    echo "Usage: $0 dir N" 1>&2
    exit 1
}

dir="$1"
n="$2"

ls "$dir" |
    while read f
    do
	tmpfile=$(mktemp)
	head -"$n" "$dir/$f" > "$tmpfile"
	mv "$tmpfile" "$dir/$f"
    done

