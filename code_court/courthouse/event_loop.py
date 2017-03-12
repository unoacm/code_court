from time import sleep

try:
    while True:
        print("We're looping!")
        sleep(30)
except KeyboardInterrupt:
    print("Event loop shutting down")
