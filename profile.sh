# run profiling

set -e

operf -g $@
opreport -l -t 1
