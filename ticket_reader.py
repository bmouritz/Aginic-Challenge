import json
import argparse
import sqlite3
import re


def main(file_name):
    conn_database(file_name)


# Try connect to database, if successful load data and push to SQLite tables, else throw error
def conn_database(filename):
    try:
        conn = sqlite3.connect('activities.db')
        cursor = conn.cursor()
        print("Successfully Connected to SQLite")

        # create tables if don't exist
        create_tables(cursor)
        # return loaded data
        data = load_json(filename)
        # insert data into tables
        insert_data(cursor, filename, conn)

        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if conn:
            conn.close()
            print("The SQLite connection is closed")


# Load JSON file
def load_json(filename):
    file = open(filename, 'r')
    return json.loads(file.read())


# Insert data into SQLite db
def insert_data(cursor, filename, conn):
    data = load_json(filename)
    load_metadata(data, cursor)
    load_activities(data, cursor)
    load_activity(data, cursor)
    load_note(data, cursor)


# Load metadata into table
def load_metadata(data, cursor):
    metadata = []
    for key, value in data['metadata'].items():
        # Iterate through key, values for dates and format them into yyyy-mm-dd HH:MM:SS
        if key != "activities_count":
            value = value[6:10] + "-" + value[3:5] + "-" + value[0:2] + " " + value[11:19]
        metadata.append(value)
    cursor.execute('INSERT INTO metadata (start_at, end_at, activities_count) '
                         'VALUES (:start_at,:end_at,:activities_count)', metadata)
    metadata.clear()


# Load activities into table
def load_activities(data, cursor):
    activities_list = []
    activities_id = 1

    # Get last metadata_id loaded as all following activities will be linked to this id
    cursor.execute('SELECT metadata_id FROM metadata ORDER BY metadata_id DESC LIMIT 1')
    # clean symbols from select statement
    metadata_id = re.sub("\D","",str(cursor.fetchall()))

    # Get last activities_id loaded as all following activities will be higher than this id
    cursor.execute('SELECT activities_id FROM activities_data ORDER BY activities_id DESC LIMIT 1')
    activity_ids = cursor.fetchall()
    # Check if array is empty
    if activity_ids:
        activities_id = int(re.sub("\D","",str(activity_ids[0]))) + 1
    ticket_id = 0

    # iterate through dict to load each row into table
    for activity in data['activities_data']:
        # iterate through inner key, values to find ticket_id to use as FK
        for key, value in activity.items():
            # Change date format if performed at key
            if key == "performed_at":
                value = str(value[6:10] + "-" + value[3:5] + "-" + value[0:2] + " " + value[11:19])
            # Get ticket_id for FK
            if key == "ticket_id":
                ticket_id = value
            # Ignore nested activity list
            if key != "activity":
                activities_list.append(value)
        activities_list.append(activities_id)
        # add in all activities_data
        cursor.execute('INSERT INTO activities_data (performed_at, ticket_id, performer_type, performer_id, activities_id) '
                             'VALUES (:performed_at, :ticket_id, :performer_type, :performer_id, ?)', (activities_list[0], activities_list[1], activities_list[2], activities_list[3], activities_list[4]))

        # add in fk if ticket_id is the same
        cursor.execute('UPDATE activities_data SET metadata_id= ? WHERE activities_id=? AND ticket_id = ?', (metadata_id, activities_list[4], ticket_id))
        activities_list.clear()
        # Manually increment activities_id
        activities_id += 1


# Load activity into table
def load_activity(data, cursor):
    temp = []
    ticket_id = 0
    i = 1
    # Get last activity_id
    cursor.execute('SELECT activity_id FROM activity ORDER BY activity_id DESC LIMIT 1')
    activity_id = cursor.fetchall()
    # Check if empty list, if it is continue, else i is now the activity_id
    if activity_id:
        i = int(re.sub("\D","",str(activity_id[0]))) + 1

    # Iterate through dict
    for activity in data['activities_data']:
        # Find ticket_id for use as FK
        for k, v in activity.items():
            if k == "ticket_id":
                ticket_id = v
        # iterate through inner list
        for key, value in activity['activity'].items():
            # Find if activity has nested note
            if key == "note":
                temp.append("True")
                break
            else:
                temp.append(value)

        # If note present, will return empty parameters, check if note exists seeing if first item in list is True
        if temp[0] != "True":
            # Insert data into table if not a note
            cursor.execute('INSERT INTO activity (shipping_address, shipment_date, category, contacted_customer, issue_type, source, status, priority, "group", agent_id, requester, product) '
                    'VALUES (:shipping_address,:shipment_date,:category,:contacted_customer,:issue_type,:source,:status,:priority,:group,:agent_id,:requester, :product)', (temp))
        else:
            # Insert data into table if a note
            cursor.execute('INSERT INTO activity (note)''VALUES(:note)', temp)

        # Insert FK by getting list of PK's in activities_data and regex string back to int
        cursor.execute("UPDATE activity SET ticket_id = ?, activities_id = ? WHERE activity_id = ?", (ticket_id, i, i))
        i += 1
        temp.clear()


# load notes into table
def load_note(data, cursor):
    temp_list = []
    i = 0
    cursor.execute('SELECT activity_id FROM activity ORDER BY activity_id DESC LIMIT 1')
    activity_id = cursor.fetchall()
    # Check if empty list, if it is continue, else i is now the activity_id
    if activity_id:
        i = int(re.sub("\D","",str(activity_id[0]))) + 1

    for a in data['activities_data']:
        for key, value in a['activity'].items():
            # Find if activity has nested note
            if key == "note":
                # If it has note, iterate through inner items
                for k, v in value.items():
                    temp_list.append(v)
                    if k == "id":
                        activity_id = v
        # Clear empty lists but retain int(0) if in list
        note_list = list(filter(lambda x: x == 0 or x, temp_list))
        # If no note present, can return empty note_temp_list2 list, so if empty do not execute insert
        if note_list:
            cursor.execute('INSERT INTO note (id, "type") ''VALUES (:id, :type)',  note_list)
            if activity_id > 0:
                # Ddd in FK
                cursor.execute('UPDATE note SET activity_id = ? WHERE id = ?', (i + 1, activity_id))
        i += 1
        note_list.clear()
        temp_list.clear()


# create tables in SQLite db
def create_tables(cursor):
    metadata_table = """CREATE TABLE IF NOT EXISTS metadata(
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    start_at TEXT NOT NULL, 
    end_at TEXT NOT NULL, 
    activities_count INTEGER NOT NULL)"""

    activities_data_table = """CREATE TABLE IF NOT EXISTS activities_data(
        activities_id INTEGER,
        ticket_id INTEGER, 
        performed_at TEXT NOT NULL,
        performer_type TEXT NOT NULL,
        performer_id INTEGER NOT NULL,
        metadata_id INTEGER,
        PRIMARY KEY (activities_id, ticket_id),
        FOREIGN KEY(metadata_id) REFERENCES metadata (metadata_id))"""

    activity_table = """CREATE TABLE IF NOT EXISTS activity(
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipping_address TEXT ,
        shipment_date TEXT,
        category TEXT,
        contacted_customer BOOL,
        issue_type TEXT,
        source INTEGER,
        status TEXT,
        priority INTEGER,
        'group' TEXT,
        agent_id INTEGER,
        requester INTEGER,
        product TEXT,
        ticket_id INTEGER,
        activities_id INTEGER,
        note BOOL,
        FOREIGN KEY(activities_id) REFERENCES activities_data (activities_id),
        FOREIGN KEY(ticket_id) REFERENCES activities_data (ticket_id))"""

    note_table = """CREATE TABLE IF NOT EXISTS note(
        id INTEGER PRIMARY KEY, 
        'type' INTEGER NOT NULL,
        activity_id INTEGER,
        FOREIGN KEY(activity_id) REFERENCES activity (activity_id)) """

    cursor.execute(metadata_table)
    cursor.execute(activities_data_table)
    cursor.execute(activity_table)
    cursor.execute(note_table)


if __name__ == "__main__":
    # Get cmdline args, filename, define argv name and defaults
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="file_name", default="activities.json", help="Name of input file")
    args = parser.parse_args()
    main(args.file_name)
