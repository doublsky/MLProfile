import numpy as np
import time

a = np.random.rand(1024, 1024)
b = np.random.rand(1024, 1024)

start = time.time()
np.dot(a, b)
end = time.time()

print "Elapsed time:", end-start, "sec"
print "GFLOPS:", 1024*1024*1024*2/(end-start)/1000000000
