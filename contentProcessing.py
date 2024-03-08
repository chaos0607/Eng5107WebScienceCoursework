
from collections import Counter, defaultdict
import glob
import json
import os
import re, emoji
import demoji
from datetime import datetime
import string

MIN_TWEET_LENGTH = 3
MIN_TOKEN_LENGTH = 3
stopwords = []

class Filter():
    # pattern = re.compile('[\W_]+')

    def is_valid_token(token):
        # we may need to add more contsraints
        # print(token, '   ', type(token))
        try:
            return((token not in stopwords) and(token != '&amp;') and (len(token) > MIN_TOKEN_LENGTH) )
        except Exception as e:
            return False

    def is_retweet(text):
        return text.startswith("RT @")

    #orginally code use get_emoji_regexp, which is deprecated and subsequently removed in new versions of the emoji package
    def strip_emoji(text):
        return demoji.replace(text, '')

    def remove_at(text):
        text = re.sub(r'@\S+', '', text)
        return text
    
    def remove_hashtagsymbol(text):
        text = re.sub(r'#', '', text)
        return text

    def remove_hashtags(text):
        text = re.sub(r'#\S+', '', text)
        return text
    
    def remove_url(text):
        text = re.sub(r'http\S+|www.\S+', '', text)
        return text
    
    def cleanList(text):
        text = Filter.strip_emoji(text)
        #text = Filter.remove_at(text)
        text = Filter.remove_hashtagsymbol(text)
        #text = Filter.remove_hashtags(text)
        #text = Filter.remove_url(text)
        text.encode("ascii", errors="ignore").decode()
        
        
        return text


    def normalize(token):
        if(token.startswith('#') or token.startswith('@') or token.startswith('$') or token.startswith('https')):
            return token
        if(token.startswith('T&amp')):
            return None
        s = token.lower()

        exclude = set(string.punctuation)
        s = ''.join(ch for ch in s if ch not in exclude)

        return s


    def tokenize(text):
        if(text is None):
            return None
        set1 = set()

        try:
            for i in text.split():
                # normalize first
                i = Filter.normalize(i)
                if(i is not None and Filter.is_valid_token(i) == True):
                    set1.add(i)
        except Exception as e:
            print(e)
            print(type(text))
        if(len(set1) > MIN_TWEET_LENGTH):
            return sorted(set1)
        else:
            return None

    def filterProcess(tweet):
        text = tweet['text']

        text1= Filter.cleanList(text)
        x= Filter.tokenize(text1)

        # print(x)
        return x

class cal_quality_score():

    def descriptionWeight(text):
        listTerms =  ['news', 'report', 'journal', 'write', 'editor', 'analyst', 'analysis','media', 'updates', 'stories', 'trader', 'investor', 'forex', 'stock', 'finance', 'market']
        listSpam = ['celebrity','ebay', 'review', 'shopping', 'deal','sale', 'sales','link', 'click', 'marketing', 'promote', 'discount', 'products', 'store', 'diet', \
        'weight', 'porn', 'followback', 'follow back', 'lucky', 'winners', 'prize', 'hiring']
        termsWeight =.1
        maxWeight = 1
        x= Filter.tokenize(text) # x is set
        if(x):
            # print(x)
            for i in x:
                maxWeight += 3
                if i in listTerms:
                    # print('in list terms : ', i)
                    termsWeight += 3
                    # print('termsWeight : ', termsWeight)
                elif i in listSpam:
                    termsWeight += 0.1
                    # print('termsWeight : ', termsWeight)
                else:
                    termsWeight += 1
            # if(termsWeight ==1):
            #         termsWeight = .1
            termsWeight = termsWeight/maxWeight
            # print('termsWeight : ', termsWeight)
        return termsWeight

    def accountAgeWeight(User):
        weight = 0
        date = datetime.today().date()

        created_at =  User['created_at']
        created_at = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')


        # datetime.strptime('Thu Apr 23 13:38:19 +0000 2009','%a %b %d %H:%M:%S %z %Y');
        daysSince = (date - created_at.date()).days
        #
        # print(daysSince)
        if daysSince < 1:
            weight = 0.05
        elif daysSince < 30:
            weight = 0.10
        elif daysSince < 90:
            weight = 0.25
        elif    daysSince > 90:
                weight = 1.0
        return weight

    def followersCount(User):
        followersCount =   User['followers_count']
        # print(followersCount)

        if followersCount < 50:
            weight = 0.5
        elif followersCount < 5000:
            weight = 1.0
        elif followersCount < 10000:
            weight = 1.5
        elif    followersCount < 100000:
            weight = 2.0
        elif    followersCount < 200000:
            weight = 2.5
        elif    followersCount > 200000:
            weight = 3.0
        return weight/3

    def verifiedUser(User):
        if (User['verified']):
            weight = 1.5
        else:
            weight = 1.0
        return weight/1.5

    def defaultProfile(User):
        weight =1
        if(User['default_profile_image']):
            weight =0.5
        return weight

    def qualityScore(self,User, text, hq_file , lq_file):

        # if(Filter.is_retweet(text)):
        #     return None
        qualityScore = 0
        profileWeight = self.defaultProfile(User)
        verifiedWeight = self.verifiedUser(User)
        followersWeight = self.followersCount(User)
        accountAgeWeight = self.accountAgeWeight(User)
        descriptionWeight = self.descriptionWeight(User['description'])
        contentWeight = self.descriptionWeight(text)


        qualityScore = (profileWeight + verifiedWeight + followersWeight + accountAgeWeight +  descriptionWeight +contentWeight)/6
        if(qualityScore>.5):
            print(qualityScore, '  ', profileWeight , '  ', verifiedWeight, '  ',followersWeight, '  ', accountAgeWeight , '  ',descriptionWeight, '   ', contentWeight)
        try:
            if (qualityScore > .79):
                hq_file.write(User['screen_name'] + '   ' + User['description'] +'\n')
                hq_file.write(str(text))
                hq_file.write(str(qualityScore)+ '  '+ str(profileWeight) + '  '+ str(verifiedWeight) + '  ' +str(followersWeight)+ '  '+ str(accountAgeWeight) + '  ' + str(descriptionWeight)+'\n')
            elif qualityScore < .48:
                lq_file.write(User['screen_name'] + '   ' + User['description']  +'\n')
                lq_file.write(str(text))
                lq_file.write(str(qualityScore)+ '  '+ str(profileWeight) + '  '+ str(verifiedWeight) + '  ' +str(followersWeight)+ '  '+ str(accountAgeWeight) + '  ' + str(descriptionWeight)+'\n')
        except Exception as e:
            print(e)
        return qualityScore

#todo: process_setting
class process_setting():
    def __init__(self,
                 MIN_TWEET_LENGTH = 3, 
                 MIN_TOKEN_LENGTH = 3, 
                 stopwords = [],
                 remove_at = 0,  
                 remove_hashtags =0, 
                 remove_url = 0, 
                 releative_threshold=2):
        self.MIN_TWEET_LENGTH = MIN_TWEET_LENGTH
        self.MIN_TOKEN_LENGTH = MIN_TOKEN_LENGTH
        self.stopwords = stopwords
        self.remove_at = remove_at
        self.remove_hashtags = remove_hashtags
        self.remove_url = remove_url
        self.releative_threshold = releative_threshold



class token_model():
    def __init__(self, json_file, token_save_path=None):
        self.total_counter = Counter()
        self.json_file = json_file

        if token_save_path is None:
            base_name = os.path.basename(json_file)
            name_without_ext = os.path.splitext(base_name)[0]
            token_save_path = f'{name_without_ext}termfreq.txt'
        '''
        #todo
        if process_setting is None:
            self.process_setting = process_setting()
        else:
            self.process_setting = process_setting
        '''

    def get_model(self):
        self.total_counter = Counter()  # Reset counter
        with open(self.json_file, 'r', encoding='utf-8') as f:
            for line in f:
                tweet = json.loads(line)
                tokens = Filter.filterProcess(tweet)
                if tokens is None: tokens = []
                self.total_counter.update(tokens)
        self.freq = sum(self.total_counter.values())

    def get_model_from_tokens(self):
        self.total_counter = Counter()  # Reset counter
        with open(self.json_file, 'r', encoding='utf-8') as f:
            for line in f:
                tweet = json.loads(line)
                tokens = tweet['text']
                tokens = self.reprocess_tokens(tokens)
                self.total_counter.update(tokens)
        self.freq = sum(self.total_counter.values())

    #todo: add process_setting's influence
    def reprocess_tokens(self, tokens):
        return tokens

    def save_tokens(self, token_save_path=None):
        if token_save_path is not None:
            self.token_save_path = token_save_path
        else:
            self.token_save_path = self.token_save_path
        with open(self.token_save_path, 'w', encoding='utf-8') as f:
            for token, freq in self.total_counter.most_common():
                f.write(f'{token}: {freq}\n')

    def print_top_tokens(self, num=50):
        for token, freq in self.total_counter.most_common(num):
            print(f'{token}: {freq}')

class single_tweet():
    def __init__(self, tweet):
        self.tweet = tweet
        self.counter = Counter()

    def get_tokens(self):
        tokens = Filter.filterProcess(self.tweet)
        if tokens is None: tokens = []
        self.counter.update(tokens)
        return tokens


if __name__ == "__main__":
    hq_file = './data/credModelFiles/highQuality.json'
    lq_file = './data/credModelFiles/lowQuality.json'
    bg_file = './data/credModelFiles/bgQuality.json'
    #token_save_path = './token_freq.txt'
    hq_model = token_model(hq_file)
    hq_model.get_model()
    hq_model.save_tokens()

    lq_model = token_model(lq_file)
    lq_model.get_model()
    lq_model.save_tokens()

    bg_model = token_model(bg_file)
    bg_model.get_model_from_tokens()
    bg_model.save_tokens()
