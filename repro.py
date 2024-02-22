from fcntl import ioctl

if ioctl(1, 2, b'qwe') == -1:
    print(42)
