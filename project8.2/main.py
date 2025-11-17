import threading


ranges = [
    [10, 20],
    [1, 5],
    [70, 80],
    [27, 92],
    [0, 16]
]


def thread_sum_range(thread_id, ranges, results):
    r = range(ranges[thread_id][0], ranges[thread_id][1] + 1)
    results[thread_id] = sum(r)


threads = []
results = [0] * len(ranges)

for i in range(len(ranges)):
    t = threading.Thread(target=thread_sum_range, args=(i, ranges, results))

    t.start()
    threads.append(t)


for t in threads:
    t.join()
    
print(results)
print(sum(results))