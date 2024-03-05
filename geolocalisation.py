from collections import Counter
import numpy as np
import json
import glob

# Path to the JSON file
json_files = glob.glob("C:/ccstudy/uofg/course/webscience/courseworks/code/data/datajson/geoLondonSep2022_*.json")

London = np.array([[-0.563, 51.261318], [0.28036, 51.686031]])\

def get_coordinates():
    
    # Counters
    total_tweets = 0
    tweets_with_location = 0
    tweets_without_location = 0

    # Array to store the coordinates
    coordinates = []

    for json_file in json_files:
        # Read the JSON file
        with open(json_file, "r", encoding='utf-8') as file:
            # Load the JSON data
            data = json.load(file)
            
            # Iterate over each tweet
            for tweet in data:
                # Increment total tweets counter
                total_tweets += 1

                # Check if the tweet has coordinates
                if "coordinates" in tweet:
                    # Increment tweets with location counter
                    tweets_with_location += 1

                    # Add the coordinates to the array
                    coordinates.append(tweet["coordinates"])
                else:
                    # Increment tweets without location counter
                    tweets_without_location += 1

    # Print the coordinates
    print(f"Total tweets: {total_tweets}")
    print(f"Tweets with location: {tweets_with_location}")
    print(f"Tweets without location: {tweets_without_location}")

    return coordinates

all_coordinates = np.array(get_coordinates())

'''
with open('coordinates.json', 'w', encoding='utf-8') as f:
    json.dump(all_coordinates, f)
'''

in_london = (all_coordinates[:, 0] >= London[0, 0]) & (all_coordinates[:, 0] <= London[1, 0]) & \
            (all_coordinates[:, 1] >= London[0, 1]) & (all_coordinates[:, 1] <= London[1, 1])

coordinates_in_london = all_coordinates[in_london]

print(coordinates_in_london.shape)

max = np.max(all_coordinates[:,0])
min = np.min(all_coordinates[:,0])
print(max,min)


max = np.max(all_coordinates[:,1])
min = np.min(all_coordinates[:,1])
print(max,min)


# Count the occurrences of each value
counter = Counter(all_coordinates)

# Get the five most common values
most_common = counter.most_common(5)

print(most_common)

