#jumble the trigram of the input, then compare that and get the one with the highest probability
# ex. i you love -> you i love, love you i, i love you 
#compute the probability of each one



from collections import Counter, defaultdict
import re
import os
import random
import pickle


class Train_Grammar:
    
    def __init__(self):
        self.n = 3
      
        
        
        self.corpus = r"../text_files/fromwikibooks.txt"
        self.corpus2 = r"../text_files/booksAndresearches.txt"
        self.corpus3 = r"../text_files/book.txt"
        # self.projectGuntenberg = r"../text_files/PG-book.txt"
        self.test = r"../text_files/bg_test.txt"
        self.trigram_probab = r"../text_files/trigram_probs.txt"
        
        self.total_words = 0
        
        self.unigramFreq = r"./text_files/unigram_frequency.txt"
        self.bigramFreq = r"./text_files/bigram_frequency.txt"
        self.trigramFreq = r"./text_files/trigram_frequency.txt"
        
        self.unigramProb = r"./text_files/unigram_probs.txt"
        self.bigramProb  = r"./text_files/bigram_probs.txt"
        self.trigramProb  = r"./text_files/trigram_probs.txt"
        
        
    def normalize_ngram_key(self,key_str: str) -> str:
        words = re.findall(r"'([^']+)'", key_str)
        if words:
            return " ".join(words)
       
        s = key_str.strip().replace("(", "").replace(")", "").replace(",", " ")
        s = re.sub(r"\s+", " ", s).strip()
        return s
        
    def load_file(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            return f.read().strip()

          
    def load_file2(self, file):
        data = {}

        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                if " : " not in line:
                    continue 

                tokens, count = line.rsplit(" : ", 1)
                data[tokens] = float(count)

        return data
    
    # def load
    
    def load_probabs(self, file):
        probabilities = {}
        
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # split from the right → only last ':' separates prob
                ngram, prob = line.rsplit(":", 1)

                ngram = ngram.strip()
                prob = prob.strip()

                tokens = tuple(ngram.split())
                probabilities[tokens] = float(prob)
        
        return probabilities

    def write_pickle(self, file, data):
       
        with open(file, "wb") as f:
            pickle.dump(data, f)
            
    def read_pickle(self, file):
        probs = {}
        with open(file, "rb") as f:  
            for line in f:
                ngram, data = line.strip().split(":", 1)
                data = eval(data)  
                probs[tuple(ngram.split())] = data["prob"]
        return probs
            
     
   
        
    
    def read_probabilities(filepath):
      
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                ngram, data = line.strip().split(":", 1)
                data = eval(data)  
                probs[tuple(ngram.split())] = data["prob"]
        return probs
    

    def read_frequencies(self, file_name):
       
        freq_dict = defaultdict(Counter)

        if not os.path.exists(file_name):
            return freq_dict

        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                if " : " not in line:
                    continue

                prefix_part, count_part = line.strip().rsplit(" : ", 1)
                tokens = prefix_part.split()
                count = float(count_part)

                if len(tokens) == 1:  
                    # unigram
                    prefix_tuple = ()
                    next_word = tokens[0]
                else:
                    # bigram/trigram
                    prefix_tuple = tuple(tokens[:-1])
                    next_word = tokens[-1]

                freq_dict[prefix_tuple][next_word] = count

        return freq_dict

    def write_frequency(self, file, file_name):
        existing = self.read_frequencies(file_name)

        # Normalize into defaultdict(Counter)
        normalized = defaultdict(Counter)
        for grams, count in file.items():
            if isinstance(grams, tuple) and len(grams) > 1:  
                prefix = grams[:-1]
                next_word = grams[-1]
            else:
                # unigram → store as () prefix + word
                prefix = ()
                next_word = grams if isinstance(grams, str) else grams[0]
            normalized[prefix][next_word] += count

        # Merge
        for prefix, counter in normalized.items():
            for word, count in counter.items():
                existing[prefix][word] += count

        # Save back
        with open(file_name, "w", encoding="utf-8") as f:
            for prefix, counter in existing.items():
                for next_word, count in counter.items():
                    if not prefix:  # unigram
                        f.write(f"{next_word} : {count}\n")
                    else:           # bi/trigram
                        prefix_str = " ".join(prefix)
                        f.write(f"{prefix_str} {next_word} : {count}\n")

     

    def write_probabilities(self, probabilities, file_name):
        """Write n-gram probabilities to file"""
        with open(file_name, "w", encoding="utf-8") as f:
            for grams, prob in probabilities.items():
                f.write(f"{grams} : {prob:.6f}\n")   
            
   
            
    def sentence_split(self, text):
        text = text.replace("\r", " ").replace("\n", " ")

        return re.split(r'(?<=[.!?])\s+', text.strip())
        
       
            
    def sentence_normalization(self, sentence): #mark the beggining and end of sentences with <s> </s>
        
        sentence = re.sub(r"\s+", ' ', sentence)       # normalize whitespace
        
        # Keep apostrophes & hyphens inside words, but drop others
  
        tokens = re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*|[.,!?;:]", sentence)
       

        lowered_tokens = [tok.lower() for tok in tokens]

        return tokens,lowered_tokens
        
    def sentence_tokenization(self, sentence,special_token = True):
        splitted_sentences=self.sentence_split(sentence)
        
        self.all_tokens = []
        
        for s in splitted_sentences:
        
            _, lowered_tokens = self.sentence_normalization(s)
        
            if special_token:
                self.all_tokens.extend(["<s>"] + lowered_tokens + ["</s>"])
            else:
                self.all_tokens.extend(lowered_tokens)
        return self.all_tokens
    # def word_tokenization(seslf, sentence):
    #     pass
    def get_total_words(self):
        text = self.load_file(self.corpus)
       
        tokens = self.sentence_tokenization(text)
        # print(tokens)
        self.total_words = len(tokens)
        
        print("ttt",self.total_words)
        
        
        
    
    def ngrams(self, t, n=3):
        tokens = self.sentence_tokenization(t)
        # print("tokens:", tokens)

        ngrams = Counter()
        self.total_words = len(tokens)        # total words
        self.vocab_size = len(set(tokens))     # unique words

        for i in range(len(tokens) - n + 1): 
            grams = tuple(tokens[i:i+n])
            ngrams[grams] += 1

        # print("Total tokens:", self.total_tokens)
        # print("Vocab size:", self.vocab_size)

        return ngrams

    
    # def create_frequency_table(self,grams, n=3):
        
    #     freq = defaultdict(Counter) if n > 1 else Counter(grams)
        
    #     if n==1:
    #         return freq
        
    #     # print("GRAMS: ", grams)
        
    #     for gram, count in grams.items():
    #         prefix = tuple(gram[:-1]) #except the last words so all of the previous words
    #         next_word = gram[-1] #the last word, the word suppose to predict(?)
            
    #         freq[prefix][next_word] += count
    #     return freq
    
    def save_frequencies(self, file=None):
        
        if file is None:
            file = self.corpus
        
        text = self.load_file(file)
        
        # print(text)
        
        trigram_freq = self.ngrams(text)
        bigram_freq = self.ngrams(text,2)
        unigram_freq= self.ngrams(text,1)
        
        
        
       
       
        self.write_frequency(trigram_freq,"../text_files/trigram_frequency.txt")
        
        self.write_frequency(bigram_freq,"../text_files/bigram_frequency.txt")
        
        self.write_frequency(unigram_freq,"../text_files/unigram_frequency.txt")
        
     
        print("\n Dpne")
        
        return trigram_freq, bigram_freq, unigram_freq
       
   
    
    
    
    def unigram_probability(self):
        self.unigrams = self.load_file2(self.unigramFreq)
        
        self.get_total_words()
        
        print(self.total_words)
        
        # print(self.unigrams, "\n DONE")
        
    
        probabilities = {}
        for word, count in self.unigrams.items():
          
            probabilities[word] = count / self.total_words
        
        # self.save_frequencies("../text_files/unigram_counts.txt", self.unigram)
    
    
        self.write_probabilities(probabilities, "../text_files/unigram_probs.txt")
        return probabilities
        
    
    def bigram_probability(self):
        bg_C= self.load_file2(self.bigramFreq)
        ug_C = self.load_file2(self.unigramFreq)
        
        probabilities = {}
         # P(w| w, w) = C(bigram) / C(unigram)
        
        for bigram, bcount in bg_C.items():
            
            words = bigram.split()
            unigram = words[0]
            
            if unigram in ug_C:
                ucount = ug_C[unigram]
                
                p= bcount/ucount
         
            
            probabilities[bigram] =p
        self.write_probabilities(probabilities, "../text_files/bigram_probs.txt")
        return probabilities        
        

    def trigram_probability(self):
        bg_C= self.load_file2(self.bigramFreq)
        
        tG_C= self.load_file2(self.trigramFreq)
        
       
        probabilities={}
        
        # P(w| w, w) = C(trigram) / C(bigram)
       
        for trigram ,tcount in tG_C.items():
     
            words = trigram.split()
            bigram = " ".join(words[:2])
            
              
                
            if bigram in bg_C:
                bcount = bg_C[bigram]
                
                p = tcount / bcount
            
            
            
            probabilities[trigram] = p
        self.write_probabilities(probabilities, "../text_files/trigram_probs.txt")
        return probabilities  
    
    
    def input_unigram_probability(self,user_input):
        # self.unigrams = self.load_file2(user_input)
        
        _,_,ug_C=self.save_frequencies(user_input)
        
        self.get_total_words()
        
        print(self.total_words)
        
        # print(self.unigrams, "\n DONE")
        
    
        probabilities = {}
        for word, count in ug_C.items():
          
            probabilities[word] = count / self.total_words
        
        # self.save_frequencies("../text_files/unigram_counts.txt", self.unigram)
    
    
        # self.write_frequency(probabilities, "../text_files/unigram_probs.txt")
        return probabilities
        
    
    def input_bigram_probability(self, user_input):
        _,bg_C,ug_C= self.save_frequencies(user_input)
        print("UG: ", ug_C)
        print("BG: ", bg_C)
        probabilities = {}
         # P(w| w, w) = C(bigram) / C(unigram)
        
        for bigram, bcount in bg_C.items():
            
           
            unigram = bigram[:1]
            print(unigram)
            
            if unigram in ug_C:
                ucount = ug_C[unigram]
                
                p= bcount/ucount
         
            
                probabilities[bigram] =p
        # self.write_probabilities(probabilities, "../text_files/bigram_probs.txt")
        return probabilities        
        

    def input_trigram_probability(self,user_input):
        tG_C,bg_C,_ = self.save_frequencies(user_input)
        
      
        probabilities={}
        
        # P(w| w, w) = C(trigram) / C(bigram)
       
        for trigram ,tcount in tG_C.items():
     
            bigram =trigram[:2]
         
            if bigram in bg_C:
                bcount = bg_C[bigram]
            
                p = tcount / bcount
                
              
            
                probabilities[trigram] = p
        # self.write_frequency(probabilities, "../text_files/trigram_probs.txt")
        return probabilities  
  
   
    
    def interpolate(self,w1,w2, w3, weights= (0.2 , 0.4 ,0.4)):
        
        weights = (0.05, 0.15, 0.8)
        
        # P(w₃ | w₁, w₂) = λ₁ × P(w₃) + λ₂ × P(w₃ | w₂) + λ₃ × P(w₃ | w₁, w₂)

        trained_unigrams_probab = self.load_probabs(self.unigramProb)
        trained_bigram_probab = self.load_probabs(self.bigramProb)
        trained_trigram_probab= self.load_probabs(self.trigramProb)
        # print(trained_unigrams_probab)
        
        # print(trained_trigram_probab)
        
        prob1 = trained_unigrams_probab.get((w3,),0)
        prob2 = trained_bigram_probab.get((w2,w3),0)
        prob3  = trained_trigram_probab.get((w1, w2, w3), 0)
        
        print("P1: ",prob1)
        print("P2: ", prob2)
        print("P3: ", prob3)
        
        interpolation = (prob1 * weights[0])+(prob2 * weights[1]) + (prob3 * weights[2])
        
        return interpolation
    
    def get_suspicious_grammars(self, tokens, suspicious , threshold=1e-5, top_k=3):
      
        print(tokens)
      
 
        w1,w2,w3= tokens
        
        
        
        score = self.interpolate(w1,w2,w3)
        
        print(score)
        
        if score < threshold:
            suspicious.append(((w1, w2, w3), score))
            
        print("SUS: ",suspicious)
        
    
    def suggest_corrections(self, sus_list  ,top_k=3):
        suggestions=[]
        
        trained_trigrams=  self.load_probabs(self.trigramProb)
        vocabulary = set([w for trigram in trained_trigrams.keys() for w in trigram])

        for trigram, score in sus_list:
            w1, w2, w3 = trigram
            
            candidates = set()
            
            for (t1, t2, t3) in trained_trigrams.keys():
                if t1 == w1 and t3 == w3:
                    candidates.add(t2)
                    
            scored_candidates = []
            for candidate in candidates:
                candidate_score = self.interpolate(w1, candidate, w3)
                scored_candidates.append((candidate, candidate_score))
                    
                    
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            top_suggestions = [c[0] for c in scored_candidates[:top_k]]

            suggestions.append({
                "trigram": trigram,
                "original_score": score,
                "suggestions": top_suggestions
            })
            
        print(suggestions)
        return suggestions
        
            
    
    def main(self, user_input):
        
        self.suspicious=[]
        
        tokens=self.ngrams(user_input)
        
        for i in tokens:
      
            sus = self.get_suspicious_grammars(i, self.suspicious)
        
        suggest = self.suggest_corrections(self.suspicious)
           
          
           
          
          
grammar_model = Train_Grammar()
# user_input = input("Enter: ")
# ss = grammar_model.save_frequencies()
# ss = grammar_model.unigram_probability()
# ss1 = grammar_model.bigram_probability()
# ss2 = grammar_model.trigram_probability()
# ss = grammar_model.read_frequencies("../text_files/trigram_frequency.txt")
# print("OP: ",ss)  

# p = grammar_model.write_pickle("trigram_prob.pkl","../text_files/trigram_probs.txt")

# user_input = input("Enter: ")