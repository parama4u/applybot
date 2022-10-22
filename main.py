import datetime

import LinkedIn.main

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    print(f"Starting at{datetime.datetime.now()}")
    LinkedIn.main.LINKEDIN().apply()
    print(f"Finished at{datetime.datetime.now()}")
