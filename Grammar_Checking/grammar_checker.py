
from collections import Counter, defaultdict
import re
import os
import random
import math

from Grammar_Checking.grammar_training import Train_Grammar

class Grammar_Checker:
    
    def __init__(self):
        
        self.tg = Train_Grammar()
        
    
    def edit_distance(self,a,b):
        
        dp = [[i + j if i * j == 0 else 0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]
        for i in range(1, len(a) + 1):
            for j in range(1, len(b) + 1):
                dp[i][j] = min(
                    dp[i-1][j] + 1,
                    dp[i][j-1] + 1,
                    dp[i-1][j-1] + (0 if a[i-1] == b[j-1] else 1)
                )
        return dp[-1][-1]

    
    
    def interpolate(self,w1,w2, w3, weights= (0.1 , 0.4 ,0.4)):
        
        weights = (0.05, 0.15, 0.8)
        
        # P(w₃ | w₁, w₂) = λ₁ × P(w₃) + λ₂ × P(w₃ | w₂) + λ₃ × P(w₃ | w₁, w₂)

        trained_unigrams_probab = self.tg.load_probabs(self.tg.unigramProb)
        trained_bigram_probab = self.tg.load_probabs(self.tg.bigramProb)
        trained_trigram_probab= self.tg.load_probabs(self.tg.trigramProb)
        # print(trained_unigrams_probab)
        
        # print(trained_trigram_probab)
        
        prob1 = trained_unigrams_probab.get((w3,),0)
        prob2 = trained_bigram_probab.get((w2,w3),0)
        prob3  = trained_trigram_probab.get((w1, w2, w3), 0)
        
        # print("P1: ",prob1)
        # print("P2: ", prob2)
        # print("P3: ", prob3)
        
        interpolation = (prob1 * weights[0])+(prob2 * weights[1]) + (prob3 * weights[2])
        
        return interpolation
    
    def get_suspicious_grammars(self, tokens, suspicious , threshold=1e-5, top_k=3):
      
        # print(tokens)
      
 
        w1,w2,w3= tokens
        
        
        
        score = self.interpolate(w1,w2,w3)
        
        # print(score)
        
        if score < threshold:
            suspicious.append(((w1, w2, w3), score))
            
        # print("SUS: ",suspicious)
        
        return suspicious
        
        
        
    def suggest_corrections(self, sentence_tokens, top_k=10):
        all_suggestions = []

    # Helper to filter out sentence boundary tokens
        def clean_ngram(ngram):
            return [w for w in ngram if w not in ("<s>", "</s>")]

        # Load n-grams
        trained_bigrams = self.tg.load_probabs(self.tg.bigramProb)
        trained_trigrams = self.tg.load_probabs(self.tg.trigramProb)

        # Process each token/phrase in the input
        for token_item in sentence_tokens:
            if isinstance(token_item, tuple) and isinstance(token_item[0], tuple):
                words_tuple, _prob = token_item
            else:
                words_tuple = token_item

            words_set = set(words_tuple)

            # Collect matching bigrams
            bigram_suggestions = []
            for words in trained_bigrams.keys():
                if len(words) == 2 and any(w in words_set for w in words):
                    cleaned = clean_ngram(words)
                    if cleaned:
                        bigram_suggestions.append(" ".join(cleaned))

            # Collect matching trigrams
            trigram_suggestions = []
            for words in trained_trigrams.keys():
                if len(words) == 3 and any(w in words_set for w in words):
                    cleaned = clean_ngram(words)
                    if cleaned:
                        trigram_suggestions.append(" ".join(cleaned))

            # Limit suggestions
            bigram_suggestions = bigram_suggestions[:top_k]
            trigram_suggestions = trigram_suggestions[:top_k]

            all_suggestions.append({
                "phrase": " ".join(words_tuple),
                "suggestions": bigram_suggestions + trigram_suggestions
            })

        return all_suggestions
        
                        
    
    def grammar_check(self, user_input):
        
        self.suspicious=[]
        
        tokens=self.tg.ngrams(user_input)
        
        for i in tokens:
      
            sus = self.get_suspicious_grammars(i, self.suspicious)
        
        # print("\n")
        # print("USER INPUT: ",user_input)
        # print("\n") 
        suggestions = self.suggest_corrections(self.suspicious)
         
        # print(suggestions)
        return suggestions
        
         
    
grammar_checker = Grammar_Checker()

    
        
        
            
        
        
    
