#!/bin/bash
if [ $# -ne 2 ]; then
	echo "usage: $0 <path/to/graph.cct> <path/to/graph.gml>"
	exit 1
fi
build_call_tree.py $1 | gv2gml | sed 's/&#45;/-/g;s/&gt;/>/' > $2
