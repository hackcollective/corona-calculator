# corona-calculator
Visualize the prevalence and predicted spread of corona virus near you.

Go to https://corona-calculator.herokuapp.com to see the app (which is continuously deployed from `Master`).

## Setup venv
```
python3 -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Running the app
```
export PORT = 8895
sh setup.sh
streamlit run corona-calculator.py
```

## Fetching live data
- Heroku Scheduler runs the `fetch_live_data.py` script to fetch live data.
