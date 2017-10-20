# run profiling

set -e

operf $@
opreport -l -t 1
#opreport -c -o call_graph.txt
