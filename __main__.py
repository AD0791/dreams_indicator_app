import sys
from streamlit import cli as stcli

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "./app/v22/dreams_indicator.py"]
    sys.exit(stcli.main())