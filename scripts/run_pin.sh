set -e
export OMP_NUM_THREADS=1
$PIN_ROOT/pin -t pintools/obj-intel64/procatrace.so -- python benchmark/bench_gemm.py
