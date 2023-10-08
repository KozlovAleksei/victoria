import mlb
import time

test = True
# test = False

if __name__ == '__main__':
    if test:
        # mlb.main(test)
        # pass

        while True:
            try:
                mlb.main(test)
            except Exception as error:
                print(error)
                time.sleep(11)

    else:
        while True:
            try:
                mlb.main(test)
            except Exception as error:
                print(error)
                time.sleep(11)
