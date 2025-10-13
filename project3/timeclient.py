import socket
import time

def system_seconds_since_1900():
    """
    The time server returns the number of seconds since 1900, but Unix
    systems return the number of seconds since 1970. This function
    computes the number of seconds since 1900 on the system.
    """

    # Number of seconds between 1900-01-01 and 1970-01-01
    seconds_delta = 2208988800

    seconds_since_unix_epoch = int(time.time())
    seconds_since_1900_epoch = seconds_since_unix_epoch + seconds_delta

    return seconds_since_1900_epoch



s = socket.socket()

s.connect(('time.nist.gov', 37))

data = s.recv(16)  # 16 should be more than enough

s.close()

time_from_gov = int.from_bytes(data, "big")

print("NIST Time  : ", time_from_gov)
print("System Time: ", system_seconds_since_1900())

