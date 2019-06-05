import os

bin_path = r'/usr/local/bin/epd'

name = os.path.basename(bin_path)
print(name)
dirname = os.path.dirname(bin_path)
print(dirname)