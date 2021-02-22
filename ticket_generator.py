import argparse
import json
from datetime import datetime, timedelta
from random import randrange, random
import random


def main(amount, file_name):
    write_data(create_tickets(amount), file_name)


# Create the tickets
def create_tickets(amount):
    dates = get_dates()
    ticket_number = randrange(1000)
    data = {'metadata': {
        'start_at': dates['start_at'],
        'end_at': dates['end_at'],
        'activities_count': amount
    }, 'activities_data': []}

    # For amount of tickets requested, make real data
    for i in range(int(amount)):
        data['activities_data'].append(populate_activities(i, ticket_number))

    return data


# Creating the activities_data metadata and activity
def populate_activities(x, ticket_number):
    date = get_dates()
    performer = randrange(140000, 150000)
    activities_data = {
        'performed_at': date['in_between'],
        'ticket_id': ticket_number + x,
        'performer_type': "user",
        'performer_id': performer,
        'activity': populate_activity(performer)
    }

    return activities_data


# Create activity
def populate_activity(performer):
    id_range = randrange(1000000, 100000000)
    ranges = randrange(10000, 100000)
    notes_required = randrange(2)
    date = get_dates()

    activity_data = {
        "shipping_address": "N/A",
        "shipment_date": date['shipped_on'],
        "category": "Phone",
        "contacted_customer": "True",
        "issue_type": "Incident",
        "source": random_range(),
        "status": status_choice(),
        "priority": random_range(),
        "group": "refund",
        "agent_id": performer,
        "requester": ranges,
        "product": "mobile"
    }

    # Chance for a note to be added instead of the activity
    for i in range(notes_required):
        activity_data = {'note': {
            "id": id_range,
            "type": random_range()}
        }

    return activity_data


# Return random choice from available list
def status_choice():
    status = ['Open', 'Closed', 'Resolved', 'Waiting for Customer', 'Waiting for Third Party', 'Pending']
    return random.choice(status)


# Return random range between 0 & 10
def random_range():
    return randrange(10)


# Return dates used in file
def get_dates():
    date_input = datetime.now()
    end_at = datetime(date_input.year,
                      date_input.month,
                      date_input.day,
                      date_input.hour,
                      date_input.minute,
                      date_input.second)
    start_at = end_at - timedelta(hours=23, minutes=59, seconds=59)
    in_between = end_at - timedelta(hours=randrange(23), minutes=randrange(59), seconds=randrange(58))
    shipped_on = end_at.strftime("%d %b, %Y")
    formatted_dates = {
        "start_at": format_date(start_at) + " +0000",
        "end_at": format_date(end_at) + " +0000",
        "in_between": format_date(in_between) + " +0000",
        "shipped_on": shipped_on
    }

    return formatted_dates


# Return a formatted date
def format_date(date):
    return date.strftime("%d-%m-%Y %H:%M:%S %z")


# Write data to file and make 'pretty'
def write_data(data, file_name):
    with open(str(file_name), 'w') as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == "__main__":
    # Get cmdline args, amount of tickets // filename, define argv name and defaults
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", dest="amount", default=4, help="Amount of tickets")
    parser.add_argument("-o", "--output", dest="file_name", default="activities.json", help="Name of output file")
    args = parser.parse_args()
    main(args.amount, args.file_name)
