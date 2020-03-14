# corona-calculator
Visualize the prevalence and predicted spread of corona virus near you.

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
streamlit run app.py
```

## Fetching live data
- To run the fetch data script every hour, add following line to `crontab -e` file:
```
0 * * * * $CODE_DIR/.venv/bin/python $CODE_DIR/fetch_live_data.py
```
- The command above runs the fetch data script with the virtualenv Python.