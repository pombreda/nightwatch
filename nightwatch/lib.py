import sys
import threading

def parallelize(iterable):
    results = {}
    def threadfunc(i, func):
        try:
            res = func()
        except Exception:
            results[i] = (False, sys.exc_info())
        else:
            results[i] = (True, res)
    
    threads = []
    for i, func in enumerate(iterable):
        thd = threading.Thread(target = threadfunc, args = (i, func))
        thd.start()
    for thd in threads:
        thd.join()
    
    output = [None] * len(results)
    for i in range(len(results)):
        succ, obj = results[i]
        if succ:
            output[i] = obj
        else:
            t, v, tb = obj
            raise t, v, tb
    return output













