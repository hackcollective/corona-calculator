# corona-calculator
Visualize the prevalence and predicted spread of corona virus near you. See our [introductory blogpost](https://towardsdatascience.com/should-i-go-to-brunch-an-interactive-tool-for-covid-19-curve-flattening-6ab6a914af0) for more details.

Go to https://corona-calculator.herokuapp.com to see the app. 

Merges to `master` are continuously deployed to http://corona-calculator-staging.herokuapp.com/

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
