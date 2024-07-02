import sys

start = int(sys.argv[1])
end = int(sys.argv[2])
total = sum(range(start, end + 1))

print(f"Sum from {start} to {end} is {total}")