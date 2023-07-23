import sys
import epp_history

if __name__ == '__main__':
    epp_history = epp_history.Client(argv=sys.argv)
    epp_history.start()
