import json
import os
import urllib.request
from datetime import datetime
import csv

data_file = "data.csv"
worksheet_name = "Sheet"
servers_file = "servers.txt"

# data should adhere to these conditions:
# - First column should be the URLs starting on row 2
# - Second column should be the URLs loader type starting on row 2
# - Every column beyond should be a timestamp as the first row,
#    followed by a player count for each server that was pinged
data = []
if os.path.isfile(data_file):
    with open(data_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

# gather every server in the servers file into a list
with open(servers_file, 'r') as f:
    servers = [line.strip() for line in f.readlines()]

# find the next column that should be used for this data entry. if it's empty, append the headers
column = 2
if len(data) > 0:
    if len(data[0]) > 2:
        column = len(data[0])
else:
    data.append(["URL", "Loader"])

# get the current time and write it to the first row in the current column
data[0].insert(column, datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

# iterate over the list of urls
for i, server in enumerate(servers):
    # every line in servers.txt should be in format "<URL> <loader>" ex: "localhost Fabric"
    splitter = server.split(" ")
    url = splitter[0]
    loader = splitter[1]

    try:
        # ping the url to get the player count
        with urllib.request.urlopen(f'https://api.mcsrvstat.us/2/{url}') as address:
            results = json.loads(address.read().decode())
        player_count = results['players']['online']
        online_status = results['online']
    except:
        # if there was an error, set player count to 0 and online status to False
        player_count = 0
        online_status = False

    print(f"{url} {loader} - {player_count} {online_status}")

    # yeah, not proud of this part
    # attempt to find if a URL already has been added so that the player count can be appended to that row
    found = False
    for row in data:
        if url in row[0]:
            # this will fill the missing columns with empty values if necessary
            index = len(data) - 1
            for j in range(column + 1):
                if len(data[index]) < j:
                    data[index].append("")

            row.insert(column, str(player_count))
            found = True

    # if the URL was not found in a row already, append it to the last row
    if not found:
        data.append([url, loader])

        # this will fill the missing columns with empty values if necessary
        index = len(data) - 1
        for j in range(column + 1):
            if len(data[index]) < j:
                data[index].append("")

        data[index].insert(column, str(player_count))

# Write the updated data back to the CSV file
with open(data_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)
