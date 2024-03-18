# Book Tracker

Read transaction tables from sportsbooks to track sports betting progress
over time. Generates an html dashboard with statistics.

https://jackarnold84.github.io/book-tracker/


**To update:**  
- Paste data from sportsbook transaction tables into [`raw_data/`](/raw_data/) directory
- Run `python run.py read` to read and process new data from [`raw_data/`](/raw_data/)
  - Note: set latest read locations in [`read/config.py`](read/config.py)
- Run `python run.py build` to rebuild site
