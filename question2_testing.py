import contentProcessing
import newsworthy

from nltk.corpus import stopwords
import spacy
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

empty_stopwords = []




def q2_test(MIN_TWEET_LENGTH,MIN_TOKEN_LENGTH,stopwords,releative_threshold,hq_model, lq_model, bg_model):
        
        contentProcessing.MIN_TWEET_LENGTH = MIN_TWEET_LENGTH
        contentProcessing.MIN_TOKEN_LENGTH = MIN_TOKEN_LENGTH
        contentProcessing.stopwords = stopwords     
        newsworthy.releative_threshold = releative_threshold

        hq_model.get_model()
        lq_model.get_model()
        bg_model.get_model_from_tokens()
        nw = newsworthy.newsWorthiness(hq_model, lq_model, bg_model)       
        newsworthy.evaluate_score_result(nw)

if __name__ == "__main__":

    hq_file = './data/credModelFiles/highQuality.json'
    lq_file = './data/credModelFiles/lowQuality.json'
    bg_file = './data/credModelFiles/bgQuality.json'
    test_file = './merged.json'

    hq_model = contentProcessing.token_model(hq_file)
    lq_model = contentProcessing.token_model(lq_file)
    bg_model = contentProcessing.token_model(bg_file)

    test = 1

    def run_test(test = test):
        if test == 1:
            q2_test(3,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.7611717974180735 err_rate: 0.17204568023833167 Absolute average: 2.5412671061200323
            hq_model.save_tokens("test1.freq")

        elif test == 2:
            q2_test(3,5,empty_stopwords,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.7172293942403177 err_rate: 0.13530287984111222 Absolute average: 2.640088608446869
        elif test == 3:
            q2_test(3,10,empty_stopwords,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.0429493545183714 err_rate: 0.002730883813306852 Absolute average: 0.18148840213495213
        elif test == 4:
            q2_test(3,0,empty_stopwords,3,hq_model,lq_model,bg_model)
            #Accuracy: 0.6889275074478649 err_rate: 0.16534260178748758 Absolute average: 2.368717017767772  

        elif test == 5:
            q2_test(0,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.7631578947368421 err_rate: 0.17229394240317775 Absolute average: 2.54542986949618
        elif test == 6:
            q2_test(5,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.6899205561072492 err_rate: 0.1564051638530288 Absolute average: 2.4626617056098645
        elif test == 7:
            q2_test(10,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.4215491559086395 err_rate: 0.046176762661370406 Absolute average: 2.4870959878599384 

        elif test == 8:
            nltk_stop_words = set(stopwords.words('english'))
            print(nltk_stop_words)
            q2_test(3,3,nltk_stop_words,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.7398212512413108 err_rate: 0.19339622641509435 Absolute average: 2.5643720648798793  
        elif test == 9:
            nlp = spacy.load('en_core_web_sm')
            spacy_stop_words = nlp.Defaults.stop_words
            print(spacy_stop_words)
            q2_test(3,3,spacy_stop_words,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.7284011916583912 err_rate: 0.2058093346573982 Absolute average: 2.5880408862212967 
            hq_model.save_tokens("test9.freq")
        elif test == 10:
            scikit_stop_words = ENGLISH_STOP_WORDS
            print(scikit_stop_words)
            q2_test(3,3,scikit_stop_words,2,hq_model,lq_model,bg_model)
            #Accuracy: 0.7452830188679245 err_rate: 0.19041708043694142 Absolute average: 2.584295968894864
        
        elif test == 11:
            q2_test(3,3,empty_stopwords,1.5,hq_model,lq_model,bg_model)
            #Accuracy: 0.7720953326713009 err_rate: 0.17105263157894737 Absolute average: 2.541841821274103
        elif test == 12:
            q2_test(3,3,empty_stopwords,1,hq_model,lq_model,bg_model)
            #Accuracy: 0.7996524329692155 err_rate: 0.16807348560079444 Absolute average: 2.5255920964865664
        elif test == 13:
            q2_test(3,3,empty_stopwords,0.5,hq_model,lq_model,bg_model)
            #Accuracy: 0.8185203574975174 err_rate: 0.16534260178748758 Absolute average: 2.4600328410377768
        elif test == 14:
            q2_test(3,3,empty_stopwords,0,hq_model,lq_model,bg_model)
            #Accuracy: 0.8252234359483615 err_rate: 0.16335650446871897 Absolute average: 2.374067664197144
        elif test == 15:
            q2_test(3,3,empty_stopwords,2.5,hq_model,lq_model,bg_model)
            #Accuracy: 0.7385799404170804 err_rate: 0.1708043694141013 Absolute average: 2.582501531934058
        elif test == 16:
            q2_test(3,3,empty_stopwords,3,hq_model,lq_model,bg_model)
            #Accuracy: 0.7264150943396226 err_rate: 0.17154915590863953 Absolute average: 2.568919975949908
        
        elif test == 17:
            #q2_test(3,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #remove '@xxx' from tokens
            #Accuracy: 0.7552135054617676 err_rate: 0.1685700099304866 Absolute average: 2.543423123885329
            pass
        elif test == 18:
            #q2_test(3,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #remove '#' from tokens
            #Accuracy: 0.7706057596822244 err_rate: 0.16931479642502484 Absolute average: 2.553174704476823
            pass   
        elif test == 19:
            #q2_test(3,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #remove '#xxx' from tokens
            #Accuracy: 0.7542204568023834 err_rate: 0.1673286991062562 Absolute average: 2.5675847819967803
            pass
        elif test == 20:
            #q2_test(3,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #remove url from tokens
            #Accuracy: 0.7465243296921549 err_rate: 0.1641012909632572 Absolute average: 2.5648673761235705
            pass
        elif test == 21:
            #q2_test(3,3,empty_stopwords,2,hq_model,lq_model,bg_model)
            #remove all above from tokens
            #Accuracy: 0.7313803376365442 err_rate: 0.16906653426017876 Absolute average: 2.5388060548869027
            pass

        elif test == 22:
            q2_test(3,3,empty_stopwords,0.5,hq_model,lq_model,bg_model)
            #remove '#' from tokens
            #final setting
            #Accuracy: 0.82025819265144 err_rate: 0.1643495531281033 Absolute average: 2.455630801452851
        else:
            raise ValueError("selete a test settingtest")
        
    run_test(22)
 