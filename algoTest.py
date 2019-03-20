from appAlgoTime import Algo

algo = Algo()

print(algo.time_slice(49.4336, -79.98112, '19:25:46:0000', '20:25:46:0000'))
print(algo.time_slice(40.463435, -79.935929, "13:46:33:4000", "14:46:50:4000"))
algo.dbWrite_location(1602, 'testUser', 40.463389, -79.935918, .01, 2)
