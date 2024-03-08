from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import numpy as np
import json
import glob

map_img_path = './map.png'

class GeoLocalisation:
    # Path to the JSON file
    
    def __init__(self, json_files, geo_range):
        self.json_files = json_files
        self.geo_range = geo_range
        self.get_coordinates()
        self.check_in_geo_range()  

    
    def processdata(self):
        self.creategrid()
        self.coordinates_to_index()

    def get_coordinates(self):
        
        # Counters
        self.total_tweets = 0
        self.tweets_with_location = 0
        self.tweets_without_location = 0

        # Array to store the coordinates
        self.coordinates = []

        for json_file in self.json_files:
            # Read the JSON file
            with open(json_file, "r", encoding='utf-8') as f:
                # Load the JSON data
                data = json.load(f)
                
                # Iterate over each tweet
                for tweet in data:
                    # Increment total tweets counter
                    self.total_tweets += 1

                    # Check if the tweet has coordinates
                    if "coordinates" in tweet:
                        # Increment tweets with location counter
                        self.tweets_with_location += 1

                        # Add the coordinates to the array
                        self.coordinates.append(tweet["coordinates"])
                    else:
                        # Increment tweets without location counter
                        self.tweets_without_location += 1

        self.coordinates = np.array(self.coordinates)

        print(f"Total tweets: {self.total_tweets}")
        print(f"Tweets with location: {self.tweets_with_location}")
        print(f"Tweets without location: {self.tweets_without_location}")
        # Print the coordinates
    
    def check_in_geo_range(self):
 
        in_range = (self.coordinates[:, 0] >= self.geo_range[0, 0]) & (self.coordinates[:, 0] <= self.geo_range[1, 0]) & \
                    (self.coordinates[:, 1] >= self.geo_range[0, 1]) & (self.coordinates[:, 1] <= self.geo_range[1, 1])

        self.coordinates_in_range = self.coordinates[in_range]
        #print(self.coordinates_in_range.shape)

    def ComputeDistance(self,lon1, lat1, lon2, lat2):
        R = 6373.0

        phi1 = lat1*np.pi/180
        phi2 = lat2*np.pi/180
        delta1 = (lat2-lat1)*np.pi/180
        delta2 = (lon2-lon1)*np.pi/180
        a = np.sin(delta1/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(delta2/2)**2
        c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
        d = R*c
        return d

    def creategrid(self):
        self.rows = int(np.ceil(self.ComputeDistance(self.geo_range[0,0], self.geo_range[0, 1], self.geo_range[0, 0], self.geo_range[1,1])))
        self.cols = int(np.ceil(self.ComputeDistance(self.geo_range[0,0], self.geo_range[0, 1], self.geo_range[1,0], self.geo_range[0,1])))
        self.noofgrids = int(self.rows*self.cols)

        self.rowstep = (self.geo_range[1,1] - self.geo_range[0,1])/self.rows
        self.colstep = (self.geo_range[1,0] - self.geo_range[0,0])/self.cols
        self.rowpoints = []
        self.colpoints = []
        for i in range(self.rows):
            self.rowpoints.append(self.geo_range[0,1]+i*self.rowstep)
        for i in range(self.cols):
            self.colpoints.append(self.geo_range[0,0]+i*self.colstep)   
        #print(self.rowpoints,self.colpoints)
        #print(len(self.rowpoints),len(self.colpoints))

    
    def coordinates_to_index(self):
        self.coordinates_index = np.zeros((self.coordinates_in_range.shape[0],2))
        for i in range(self.coordinates_in_range.shape[0]):
            self.coordinates_index[i,1] = np.floor((self.coordinates_in_range[i,1] - self.geo_range[0, 1]) / self.rowstep)
            self.coordinates_index[i,0] = np.floor((self.coordinates_in_range[i,0] - self.geo_range[0, 0]) / self.colstep)

        self.heat_map = np.zeros((self.rows,self.cols))
        for i in range(self.coordinates_index.shape[0]):
            self.heat_map[int(self.coordinates_index[i,1]),int(self.coordinates_index[i,0])] += 1
        print(f"Total number in diagram:{int(np.sum(np.array(self.heat_map).flatten()))}")
        self.log_heat_map = np.log1p(self.heat_map)

    def reset_coordinates(self,coordinates):
        self.coordinates = coordinates
        self.check_in_geo_range()
        self.coordinates_to_index()

    def draw_heat_map(self):
        
        plt.figure(figsize=(10 * self.cols / self.rows, 10))  
        plt.imshow(self.log_heat_map, cmap='hot', interpolation='nearest', origin='lower') 
        plt.colorbar()
        plt.xlabel('grid_col')
        plt.ylabel('grid_row')
        plt.title('Heat Map (Log Scale)')
        plt.xticks(np.arange(0, self.cols, 2))
        plt.yticks(np.arange(0, self.rows, 2))
        plt.savefig('heatmap.png')
        plt.show()

    def draw_heat_map_on_map(self, map_img_path):
    # Load the map image
        map_img = mpimg.imread(map_img_path)

        # Create a new figure
        plt.figure(figsize=(10 * self.cols / self.rows, 10))

        # Display the map image
        plt.imshow(map_img, extent=[0, self.cols, 0, self.rows])

        # Display the heat map with a transparency of 0.5
        plt.imshow(self.log_heat_map, cmap='hot', interpolation='nearest', origin='lower', alpha=0.5, extent=[0, self.cols, 0, self.rows])

        # Add a color bar, labels, title, and save the figure
        plt.colorbar()
        plt.xlabel('grid_col')
        plt.ylabel('grid_row')
        plt.title('Heat Map on Map (Log Scale)')
        plt.xticks(np.arange(0, self.cols, 2))
        plt.yticks(np.arange(0, self.rows, 2))
        plt.savefig('heatmap_on_map.png')
        plt.show()

    def draw_distribution_map(self):
        plt.figure(figsize=(10, 5))
        plt.hist(self.heat_map.flatten(), bins=100, range=(0, 1000))
        plt.yscale('log')
        plt.xlabel('Number of tweets')
        plt.ylabel('Number of grids')
        plt.title('Distribution of the number of tweets in each grid')
        plt.show()


if __name__ == '__main__':
    def q1():
        json_files = glob.glob("./merged.json")
        London = np.array([[-0.563, 51.261318], [0.28036, 51.686031]])
        London_geo = GeoLocalisation(json_files, London)
        London_geo.processdata()
        London_geo.draw_heat_map()
        London_geo.draw_distribution_map()
        London_geo.draw_heat_map_on_map(map_img_path)
    q1()