'''
we have been given the quality so we can skip calculating it
however, we still need to do content processing
'''
import glob
import json
from matplotlib import pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix
import contentProcessing
import geolocalisation

releative_threshold = 0.5

hq_file = './data/credModelFiles/highQuality.json'
lq_file = './data/credModelFiles/lowQuality.json'
bg_file = './data/credModelFiles/bgQuality.json'

class newsWorthiness():
    def __init__(self, hq_model: contentProcessing.token_model, lq_model: contentProcessing.token_model, bg_model: contentProcessing.token_model):
        
        self.hq_model = hq_model
        self.lq_model = lq_model
        self.bg_model = bg_model

        if not self.hq_model.total_counter:
            raise ValueError("hq_model's term freq is not initialized, please run get_model() or get_model_from_tokens() first")
        if not self.lq_model.total_counter:
            raise ValueError("lq_model's term freq is not initialized, please run get_model() or get_model_from_tokens() first")
        if not self.bg_model.total_counter:
            raise ValueError("bg_model's term freq is not initialized, please run get_model() or get_model_from_tokens() first")

        self.rhqt_assist = self.bg_model.freq / self.hq_model.freq
        self.rlqt_assist = self.bg_model.freq / self.lq_model.freq

    def cal_news_worthiness_score(self,single_tweet: contentProcessing.single_tweet):
        single_tweet.get_tokens()
        score = 0
        sum_shqt = 0
        sum_slqt = 0
        for token in single_tweet.counter:
            tfthq = self.hq_model.total_counter[token]
            tftlq = self.lq_model.total_counter[token]
            tftbg = self.bg_model.total_counter[token]

            #rhqt = (tfthq/fhq) / (tftbg/fbg) # relative high quality term frequency
            #rlqt = (tftlq/flq) / (tftbg/fbg) # relative high quality term frequency
            if tftbg == 0:
                rhqt = 0
                rlqt = 0
            else:
                rhqt = tfthq/tftbg*self.rhqt_assist
                rlqt = tftlq/tftbg*self.rlqt_assist

            if (rhqt > releative_threshold):
                shqt=rhqt
            else:
                shqt=0
            sum_shqt += shqt

            if (rlqt > releative_threshold):
                slqt=rlqt
            else:
                slqt=0
            sum_slqt += slqt

        score = np.log2((1 + sum_shqt)  / (1 + sum_slqt))
        return score
    
    def score_file(self, filename,filetype=0,print_hist=False):
        scores = []

        if filetype == 0:
            with open(filename, "r", encoding='utf-8') as f:
                data = json.load(f)
                for tweet in data:
                    tweet = contentProcessing.single_tweet(tweet)
                    score = self.cal_news_worthiness_score(tweet)
                    scores.append(score)

        else:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    tweet = contentProcessing.single_tweet(json.loads(line))
                    score = self.cal_news_worthiness_score(tweet)
                    scores.append(score)
        if print_hist:
            plt.hist(scores, bins=50)
            plt.xlabel('Score')
            plt.ylabel('Frequency')
            plt.title('Distribution of News Worthiness Scores')
            plt.show()

        return scores

def evaluate_score_result(nw: newsWorthiness):

    score_hq=nw.score_file(hq_file,1)
    score_lq=nw.score_file(lq_file,1)

    score_hq = np.array(score_hq)
    hq_count = len(score_hq)
    hq_sum = np.sum(score_hq)
    hq_positive_count = np.sum(score_hq > 0)
    hq_negative_count = np.sum(score_hq < 0)

    score_lq = np.array(score_lq)
    lq_count = len(score_lq)
    lq_sum = np.sum(score_lq)
    lq_positive_count = np.sum(score_lq > 0)
    lq_negative_count = np.sum(score_lq < 0)

    accuracy = (hq_positive_count + lq_negative_count) / (hq_count + lq_count)
    err_rate = (hq_negative_count + lq_positive_count) / (hq_count + lq_count)
    abs_avg =  (abs(hq_sum) + abs(lq_sum)) / (hq_count + lq_count)

    print(f"Accuracy: {accuracy}" f" err_rate: {err_rate}" f" Absolute average: {abs_avg}")



if __name__ == "__main__":

    test_file = './merged.json'
    result_file = './result.json'

    def q2():
        '''
        what 
        '''

        hq_model = contentProcessing.token_model(hq_file)
        lq_model = contentProcessing.token_model(lq_file)
        bg_model = contentProcessing.token_model(bg_file)

        hq_model.get_model()
        lq_model.get_model()
        bg_model.get_model_from_tokens()
        nw = newsWorthiness(hq_model, lq_model, bg_model)

        hq_model.save_tokens("q2_hq.term")
        lq_model.save_tokens("q2_lq.term")
        bg_model.save_tokens("q2_bg.term")
        evaluate_score_result(nw)
        #Accuracy: 0.7611717974180735 err_rate: 0.17204568023833167 Absolute average: 2.5412671061200323


    def q3():
        hq_model = contentProcessing.token_model(hq_file)
        lq_model = contentProcessing.token_model(lq_file)
        bg_model = contentProcessing.token_model(bg_file)

        hq_model.get_model()
        lq_model.get_model()
        bg_model.get_model_from_tokens()

        nw = newsWorthiness(hq_model, lq_model, bg_model)

        tweet_scores = []
        high_worthiness_tweets = []  # List to hold tweets with score > 0

        with open(test_file, "r", encoding='utf-8') as f:
            data = json.load(f)
            for tweet in data:
                tweet_obj = contentProcessing.single_tweet(tweet)
                score = nw.cal_news_worthiness_score(tweet_obj)
                if score > 0:
                    high_worthiness_tweets.append(tweet)
                if "coordinates" in tweet:
                    tweet_scores.append({'coordinates': tweet['coordinates'], 'score': score})
        

        scores_array = np.array([item['score'] for item in tweet_scores])
        coordinates_array = np.array([item['coordinates'] for item in tweet_scores])
        new_coordinates = coordinates_array[scores_array > 0]

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(high_worthiness_tweets, f, ensure_ascii=False, indent=4)

        London = np.array([[-0.563, 51.261318], [0.28036, 51.686031]])
        London_geo = geolocalisation.GeoLocalisation(glob.glob(result_file), London)
        London_geo.processdata()
        London_geo.draw_heat_map()
        London_geo.draw_distribution_map()

    q3()

