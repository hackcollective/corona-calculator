# corona-calculator

A tool to help you visualize the prevalence and predicted spread of corona virus near you, and understand how 
transmission, hospital load, and deaths are affected by social distancing. 

See our [introductory blogpost](https://towardsdatascience.com/should-i-go-to-brunch-an-interactive-tool-for-covid-19-curve-flattening-6ab6a914af0) for more details.

The modelling and data sources are documented in [Notion](https://www.notion.so/coronahack/Public-842dd2b1f6ea4123b53318ed39f6c73d).

Go to https://corona-calculator.herokuapp.com to see the app.

## Installation

The code is in Python and relies upon the [Streamlit](https://www.streamlit.io) framework to power the frontend.

To run this repo locally, do the following:

### Setup venv
```
python3 -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Running the app
```
export PORT = 8895
sh setup.sh
streamlit run corona-calculator.py
```

If you run locally without S3 credentials, data will be downloaded into this repo (see [below](#data) )

## Deployment
Deployment is via Heroku, and follows the following steps:
1. PRs are automatically deployed to Heroku, allowing others to see the effects of your changes. You should see a link 
in Github at the bottom of your PR.
2. Merges to `master` are deployed to a staging environment: https://dashboard.heroku.com/apps/corona-calculator-staging
3. Deployment to production is, for the time being, manual

## Data
Data is stored in an S3 bucket. See the [data README](./data/README.md) for details of sources.

We refresh data hourly using a Heroku scheduler job to fetch up to date case information from Johns Hopkins. This job 
runs the `fetch_live_data.py` script.

If you'd like to add data for new countries, please do! Be aware that you will need to add population and hospital
bed data. Unfortunately we're currently limited by the case data provided by the (amazing) [Johns Hopkins repo](https://github.com/CSSEGISandData/COVID-19)
: if your country isn't there, we're not going to be able to add it. 

## Contributing
We would LOVE you to contribute to this app, which is fast moving and requires continued attention as
the crisis evolves. Check out the [issues](https://github.com/archydeberker/corona-calculator/issues) for some 
suggestions of things to work on (keep an eye out for the `good first contribution` tag if you're new here.)

You'll need to [fork the repo](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork)
to make your changes, and then open an PR. We don't have PR guidelines for now - just be sensible and please bear
with us if we're slow to review as we all have full time jobs!

If you're interested in adding a major feature or change the design of the app please feel free to run it by us
(open an issue and tag us) before commencing work. Our designer will probably want to give it a once over before
any coding takes place!