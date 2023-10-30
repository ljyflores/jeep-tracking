# jeep-tracking

## Notes
* <a href="https://docs.google.com/presentation/d/1HBI2O9_CNfGgkSPSBcUgp-rGfJwl4dMcvhflibpxaxk/edit?usp=sharing">Front-End Mockups</a>
* <a href="https://docs.google.com/document/d/1W9fd7fIbHWqNY2xjkL8QkQWF4GuLpQxDbfExf7RjfAw/edit?usp=sharing">Logistics + Business Ideas</a>

## Front End 
- [ ] ID Text Box + Query BigQuery API + Enter Button (1)
- [ ] List of Arriving Jeeps (1)
- [ ] Drop-down List of Stops from Each Jeep (1)
- [ ] Notif Sounds at 5, 3, 1, 0 Mark (2)
- [ ] QR Code Link to Website (i.e. scan QR code, opens the website) (3)
- [ ] Function to save time and ID queried by commuter to BQ table (4)

## Back End
- [ ] BigQuery Table for Current ETAs (set-up + query functions) (1)
- [ ] BigQuery Table for Historical ETAs + Geolocation (set-up + query functions) (1)
- [ ] AirTag GPS (1) – ordered an AirTag!

## Feature Wishlist
- [ ] Android App
  - [ ] Let users save favorite stops
  - [ ] App badge notifs
- [ ] Ask users to verify when they got on, for us to improve predictions
- [ ] Figure out how to get users’ locations, to figure out if they’ve ridden the jeep – goal is to tell the stats
- [ ] Figure out what other companies do with commuting info, there must be a way that they leverage this which is important given that we don’t have good data for this back home

## Set-Up
### Environment
Requirements text file to come

### Google Cloud API
Goal: Be able to use Python to query the tables we have stored in BQ
* Step 1: Install the Google Cloud CLI following steps 1-4 here: https://cloud.google.com/sdk/docs/install
* Step 2: Log in and create a credential file using `./google-cloud-sdk/bin/gcloud auth application-default login` (This will lead you to sign-in online into the GMail account, sign in with AsanKa, or personal emails)
* Step 3: Set the project name using `./google-cloud-sdk/bin/gcloud config set project eco-folder-402813`
* Step 4: Pray

This is how we then query a table:
```
from google.cloud import bigquery

client = bigquery.Client(project="eco-folder-402813")

QUERY = (
    'SELECT * FROM `jeep_etas.test` '
    'LIMIT 100')
query_job = client.query(QUERY)  # API request
rows = query_job.result()  # Waits for query to finish

for row in rows:
    print(row)
```
  
* 
