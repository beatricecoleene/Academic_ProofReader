import re
import numpy as np
from collections import defaultdict, Counter
import math

class SpellChecker:
    def __init__(self, n=3, filename="words.txt", sentence="academic_corpus.txt"):
        self.n = n  # default n-gram size
        self.corpus = set()
        self.context_counts = defaultdict(int)
        self.word_freq = defaultdict(int)

        self.load_corpus(filename)
        self.load_sentences_build(sentence)
        self.memo = {}


    def load_corpus(self, filename):
        try: 
            with open(filename, "r", encoding="utf-8") as f:
                self.corpus = set(line.strip().lower() for line in f if line.strip())
                # print(self.corpus)
        except FileNotFoundError:
            print(f"{filename} not found")

        # self.corpus_ngrams = {w: self.ngrams_char(w) for w in self.corpus}

    def load_sentences_build(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.academic_sentences = [line.strip().lower() for line in f if line.strip()]
                # print(self.academic_sentences)
        except FileNotFoundError:
            print(f"{filename} not found")

        self.build_context_model(self.academic_sentences)


    def build_context_model(self, sentences):
        for sentence in sentences:
            tokens = self.tokenize(sentence.lower())

            for token in tokens:
                self.word_freq[token] += 1

            for n in [2, 3]: # bigrams and trigrams
                ngrams = self.ngrams_word(tokens, n)
                for ngram in ngrams:
                    self.context_counts[ngram] += 1

    def ngrams_word(self, tokens, n):
        result = []
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i + n])
            result.append(ngram)
        return result

    def normalize(self, text):
        text = text.lower()
        text = re.sub(r"\s+", ' ', text)              # normalize whitespace
        text = re.sub(r"[^\w\s]", '', text)           # remove non-word except spaces
        return text.strip()

    def tokenize(self, text):
        text = self.normalize(text)
        tokens = re.split(r'\s+', text.strip())
        return tokens

    def ngrams_char(self, word):
        ngrams_list = []
        padded = f"<{word}>"
        for i in range(len(padded) - self.n + 1):
            ngram = padded[i:i + self.n]
            ngrams_list.append(ngram)
        return ngrams_list
    
    # jaccard similarity -> overlapping/total unique items (intersection/union)
    # 0 if no common items, 1 if all items are common
    def jaccard_similarity(self, set1, set2):
        intersection = len(list(set(set1).intersection(set2)))
        union = (len(set1) + len(set2) - intersection)
        return float(intersection) / union if union > 0 else 0.0
    

    def levenshtein(self, s, t):
        len_s, len_t = len(s), len(t)

        dp = [[0] * (len_t + 1) for _ in range(len_s + 1)]

        for i in range(len_s + 1):
            dp[i][0] = i
        for j in range(len_t + 1):
            dp[0][j] = j

        for i in range(1, len_s + 1):
            for j in range(1, len_t + 1):
                cost = 0 if s[i - 1] == t[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1,      # deletion
                               dp[i][j - 1] + 1,    # insertion
                               dp[i - 1][j - 1] + cost) # substitution
                
                if i > 1 and j > 1 and s[i - 1] == t[j - 2] and s[i - 2] == t[j - 1]:
                    dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)

        return dp[len_s][len_t]


    def check_spell(self, word, top_k=10, filter_k=5000):
        if word in self.memo:
            return self.memo[word]
        
        word_ngrams = self.ngrams_char(word)
        scores = []

        # JACCARD
        jaccard_scores = []
        for corpus_word in self.corpus:
            corpus_ngrams = self.ngrams_char(corpus_word)
            jaccard_score = self.jaccard_similarity(word_ngrams, corpus_ngrams)
            if jaccard_score > 0:
                jaccard_scores.append((corpus_word, jaccard_score))

        
        jaccard_scores.sort(key=lambda x: x[1], reverse=True)
        jaccard_scores = jaccard_scores[:filter_k]


        # LEVENSHTEIN
        for cand, jaccard_score in jaccard_scores:
            dist = self.levenshtein(word, cand)
            max_len = max(len(word), len(cand))
            lev_score = 1 - (dist / max_len)

            score = 0.7 * lev_score + 0.3 * jaccard_score  # 70% lev, 30% jacc
            scores.append((cand, score, dist, jaccard_score))


        scores.sort(key=lambda x: (-x[1], -x[2])) # sort by score and then by distance
        results = scores[:top_k]

        self.memo[word] = results
        return results
    
    
    def get_context_score(self, candidate, tokens, word_index):
        score = 0
        total = 0

        # bigram
        if word_index > 0:
            left_bigram = (tokens[word_index - 1], candidate)
            count = self.context_counts.get(left_bigram, 0)
            weight = 2
            score += count * weight
            total += weight

        if word_index < len(tokens) - 1:
            right_bigram = (candidate, tokens[word_index + 1])
            count = self.context_counts.get(right_bigram, 0)
            weight = 2
            score += count * weight
            total += weight


        #trigram
        if 0 < word_index < len(tokens) - 1:
            left = tokens[word_index - 1]
            right = tokens[word_index + 1]
            trigram = (left, candidate, right)
            count = self.context_counts.get(trigram, 0)
            weight = 5
            score += count * weight
            total += weight


        #word freq
        word_freq = self.word_freq.get(candidate, 1)
        word_freq_score = math.log(word_freq + 1)  # log scale
        weight = 1
        score += word_freq_score
        total += weight


        return score / total if total > 0 else 0
    

    def check_context(self, word, context_tokens, word_index, top_k=5):
        if word in self.corpus:
            print(f"'{word}' is correct.")
            return [(word, 1.0, "correct", {"context_score": 0})]


        jacc_lev_candidates = self.check_spell(word, top_k=10)

        if not jacc_lev_candidates:
            return []
        
        context_cand = []

        for cand, base_score, lev_dist, jaccard in jacc_lev_candidates:
            context_score = self.get_context_score(cand, context_tokens, word_index)

            # (lev score(70%) + jacc_score(30%))(50%) + context score(50%)
            final_score = 0.5 * base_score + 0.5 * context_score

            context_cand.append((
                cand, 
                final_score, 
                f"lev:{lev_dist}", 
                {
                    "base_score": base_score,
                    "context_score": context_score,
                    "jaccard": jaccard
                }
            ))

        context_cand.sort(key=lambda x: x[1], reverse=True) 
        return context_cand[:top_k]
    


    def check_spell_with_context(self, text):

        tokens = self.tokenize(text)
        results = {}

        print(f"checking: '{text}'")

        for i, token in enumerate(tokens):
            if token not in self.corpus:
                suggestions = self.check_context(token, tokens, i)
                results[token] = suggestions

                print(f"'{token}' -> Suggestions:")
                # print(suggestions)
                for cand, score, lev, other in suggestions:
                    print(f"{cand:<20} | Final score: {score:.3f} | LevJac: {other['base_score']:.3f} | Context: {other['context_score']:.3f}")

                print('')

        print(results)
        return results

#--------------------------------------------------------------------------
if __name__ == "__main__":
    text = input("Enter text to check: ")
    sc = SpellChecker(n=3)

    suggestions = sc.check_spell_with_context(text)
    