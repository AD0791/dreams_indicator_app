import sys
from streamlit import cli as stcli

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "./app/dreams_data_application.py"]
    sys.exit(stcli.main())
    