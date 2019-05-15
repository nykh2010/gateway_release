import time

cur_time = time.time()
print(cur_time)

str_time = ""
end_time = time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S"))
print(end_time)