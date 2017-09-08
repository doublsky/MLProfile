# run profiling

set -e

operf $@
opreport -l -t 1
