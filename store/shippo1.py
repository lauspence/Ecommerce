import requests
import json
import shippo

# Set your Shippo API key
shippo.config.api_key = ""

# Create the shipment
url = "https://api.goshippo.com/shipments/"
headers = {
    "Authorization": "ShippoToken shippo_test_6b8b4da6247bd3e14c92a515b1608c982d78a52f",
    "Content-Type": "application/json"
}

payload = {
    "address_to": {
        "name": "Mr Hippo",
        "street1": "965 Mission St #572",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94103",
        "country": "US",
        "phone": "4151234567",
        "email": "mrhippo@goshippo.com"
    },
    "address_from": {
        "name": "Mrs Hippo",
        "street1": "1092 Indian Summer Ct",
        "city": "San Jose",
        "state": "CA",
        "zip": "95122",
        "country": "US",
        "phone": "4159876543",
        "email": "mrshippo@goshippo.com"
    },
    "parcels": [{
        "length": "10",
        "width": "15",
        "height": "10",
        "distance_unit": "in",
        "weight": "1",
        "mass_unit": "lb"
    }],
    "async": False
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
shipment_data = response.json()

# Get rates for the shipment
rates = shipment_data['rates']

# Set the max transit time
MAX_TRANSIT_TIME_DAYS = 3

# Filter rates by max. transit time, then select cheapest
eligible_rates = [rate for rate in rates if rate['estimated_days'] <= MAX_TRANSIT_TIME_DAYS]
if eligible_rates:
    rate = min(eligible_rates, key=lambda x: float(x['amount']))
    print("Picked service %s %s for %s %s with est. transit time of %s days" %
          (rate['provider'], rate['servicelevel']['name'], rate['currency'], rate['amount'], rate['estimated_days']))

    # Purchase the desired rate
    transaction = shippo.Transaction.create(rate=rate['object_id'], asynchronous=False)

    # Print label_url and tracking_number
    if transaction.status == "SUCCESS":
        print("Purchased label with tracking number %s" % transaction.tracking_number)
        print("The label can be downloaded at %s" % transaction.label_url)
    else:
        print("Failed purchasing the label due to:")
        for message in transaction.messages:
            print("- %s" % message['text'])
else:
    print("No eligible rates found.")   