set -e
export OMP_NUM_THREADS=1
~/Tools/pin-3.4-97438-gf90d1f746-gcc-linux/pin -t ~/Tools/pin-3.4-97438-gf90d1f746-gcc-linux/source/tools/MyPinTool/obj-intel64/procatrace.so -- python benchmark/bench_linear.py -ns 100 -nf 10
