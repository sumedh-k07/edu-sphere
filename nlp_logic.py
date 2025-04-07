import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math


import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import TfidfModel


import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.cluster.util import cosine_distance
from rake_nltk import Rake


from bs4 import BeautifulSoup
import networkx as nx
import requests
import re
import heapq






nltk.download('all', quiet=True)


stop_words = stopwords.words('english')




def scrape_data(URL):
   html_page = requests.get(URL).text
   soup = BeautifulSoup(html_page, 'lxml')
   text = soup.get_text(separator=" ", strip=True)  # Extract all text
   text = re.sub(r'\[[^\]]*\]', '', text)  # Remove citations in brackets
   text = re.sub(r"\s+", " ", text)  # Remove excess whitespace
   return text.strip()




def clean_text(text):
   text = text.lower()  # Convert to lowercase
   text = re.sub(r'\[[^\]]*\]', '', text)  # Remove citations
   text = re.sub(r"\s+", " ", text)  # Remove extra spaces
   return text.strip()




def lemmatization(texts, stop_words, allowed_postags=['NN', 'NNS', 'NNP', 'NNPS', 'RB', 'RBR', 'RBS',
                                                     'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',
                                                     'JJ', 'JJR', 'JJS']):
   lemmatizer = WordNetLemmatizer()
   texts_out = []
   for text in texts:
       try:
           words = nltk.word_tokenize(text)
           tagged_words = nltk.pos_tag(words)
           new_text = [lemmatizer.lemmatize(word) for word, tag in tagged_words
                       if word not in stop_words and tag in allowed_postags]
           texts_out.append(" ".join(new_text))
       except Exception as e:
           print(f"Error processing text: {text[:50]}... - {e}")
   return texts_out




def group_sentences(sentences, group_len=3):
   # Group sentences into blocks of group_len
   new_sentences = []
   for idx in range(0, len(sentences), group_len):
       new_sent = ''
       i = idx
       while i < len(sentences) and i < idx + group_len:
           new_sent += sentences[i] + " "
           i += 1
       new_sentences.append(new_sent.strip())
   return new_sentences




def gen_words(texts):
   # Tokenize and preprocess each grouped sentence
   final = []
   for text in texts:
       new = simple_preprocess(text, deacc=True)
       final.append(new)
   return final




def make_bigrams(bigram, texts):
   return [bigram[doc] for doc in texts]




def make_trigrams(trigram, bigram, texts):
   return [trigram[bigram[doc]] for doc in texts]




def get_topic_index(lda_model):
   cluster_idx = lda_model.show_topics()
   topics = {}
   present_topics = set()
   for term in cluster_idx:
       terms = term[1].split('+')
       for idx, item in enumerate(terms):
           element = item.split('*')[1].strip()[1:-1]
           if element not in present_topics:
               present_topics.add(element)
               topics[term[0]] = element
               break
   return topics




def get_grouped_sentences(lda_model, corpus, sentences):
   # Find the most important sentence per topic and group them
   grouped_sentences = {k: '' for k in range(0, 10)}
   lda_corpus = lda_model[corpus]
   cluster_index_list = [doc for doc in lda_corpus]
   for idx in range(len(cluster_index_list)):
       indexes = cluster_index_list[idx]
       if len(indexes) == 1:
           grouped_sentences[indexes[0][0]] += sentences[idx] + " "
       else:
           max_prob = 0
           best_index = 0
           for index in indexes:
               prob = index[1]
               if prob > max_prob:
                   max_prob = prob
                   best_index = index[0]
           grouped_sentences[best_index] += sentences[idx] + " "
   return grouped_sentences




def create_topics(text, sentence_group=3, num_topics=10, min_count=3, threshold=25):
   stop_words_local = stopwords.words('english')
   sentences = nltk.sent_tokenize(text)
   grouped_sentences = group_sentences(sentences, sentence_group)
   lemmatized_text = lemmatization(grouped_sentences, stop_words_local)
   data_words = gen_words(lemmatized_text)
   bigram_phrases = gensim.models.Phrases(data_words, min_count=min_count, threshold=threshold)
   trigram_phrases = gensim.models.Phrases(bigram_phrases[data_words], threshold=threshold)
   bigram = gensim.models.phrases.Phraser(bigram_phrases)
   trigram = gensim.models.phrases.Phraser(trigram_phrases)
   data_bigrams = make_bigrams(bigram, data_words)
   data_bigrams_trigrams = make_trigrams(trigram, bigram, data_bigrams)
   id2word = corpora.Dictionary(data_bigrams_trigrams)
   corpus = [id2word.doc2bow(text) for text in data_bigrams_trigrams]
   tfidf = TfidfModel(corpus=corpus, id2word=id2word)
   low_value = 0.03
   corpus = [[(id, value) for id, value in tfidf[bow] if value >= low_value] for bow in corpus]
   lda_model = gensim.models.LdaModel(corpus=corpus,
                                      id2word=id2word,
                                      num_topics=num_topics,
                                      random_state=42,
                                      update_every=1,
                                      chunksize=100,
                                      passes=10,
                                      alpha='auto')
   topics = get_topic_index(lda_model)
   return get_grouped_sentences(lda_model, corpus, grouped_sentences), topics




def get_important_sentences(data, num_sentences=25, stop_words_local=None):
   if stop_words_local is None:
       stop_words_local = set(stopwords.words('english'))
   sentence_tokens = nltk.sent_tokenize(data)
   word_frequencies = {}
   for word in nltk.word_tokenize(data):
       if word.lower() not in stop_words_local:
           word_frequencies[word] = word_frequencies.get(word, 0) + 1
   max_frequency = max(word_frequencies.values(), default=1)
   for word in word_frequencies:
       word_frequencies[word] /= max_frequency
   sentence_scores = {}
   for sentence in sentence_tokens:
       words = nltk.word_tokenize(sentence.lower())
       sentence_scores[sentence] = sum(word_frequencies.get(word, 0) for word in words if len(sentence.split()) < 30)
   top_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
   return [nltk.word_tokenize(sentence) for sentence in top_sentences]




def sentence_similarity(sent1, sent2, stop_words_local):
   sent1 = [w.lower() for w in sent1]
   sent2 = [w.lower() for w in sent2]
   all_words = list(set(sent1 + sent2))
   vector1 = [0] * len(all_words)
   vector2 = [0] * len(all_words)
   for w in sent1:
       if w not in stop_words_local:
           vector1[all_words.index(w)] += 1
   for w in sent2:
       if w not in stop_words_local:
           vector2[all_words.index(w)] += 1
   return 1 - cosine_distance(vector1, vector2)




def gen_sim_matrix(sentences, stop_words_local):
   similarity_matrix = np.zeros((len(sentences), len(sentences)))
   for idx1 in range(len(sentences)):
       for idx2 in range(len(sentences)):
           if idx1 == idx2:
               continue
           similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words_local)
   return similarity_matrix




def generate_summary(data, top_n=5):
   sentences = get_important_sentences(data)
   summarized_text = []
   sentence_similarity_matrix = gen_sim_matrix(sentences, stop_words)
   sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
   scores = nx.pagerank(sentence_similarity_graph)
   ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
   upper_limit = min(len(ranked_sentences), top_n)
   for i in range(upper_limit):
       summarized_text.append(" ".join(ranked_sentences[i][1]))
   summary = " ".join(summarized_text)
   return summary




def set_threshold(phrases):
   scores = [phrase[0] for phrase in phrases]
   threshold = np.percentile(scores, 65)
   return threshold




def get_common_phrases(phrase_list, max_nodes=5):
   common_phrases = []
   for group1 in phrase_list:
       flag = 0
       count_common_phrases = 0
       for phrase1 in group1:
           for group2 in phrase_list:
               if group1 != group2:
                   for phrase2 in group2:
                       if phrase1[1] == phrase2[1]:
                           common_phrases.append([phrase1[0], phrase_list.index(group1), phrase_list.index(group2)])
                           count_common_phrases += 1
                           if count_common_phrases == max_nodes:
                               flag = 1
                               break
                   if flag:
                       break
           if flag:
               break
   return common_phrases




def get_best_phrases(phrase_list, max_nodes=5):
   final_phrases = []
   for phrases in phrase_list:
       final_phrases_topic = []
       if phrases:
           threshold = set_threshold(phrases)
           for phrase in phrases:
               if phrase[0] > math.floor(threshold):
                   if final_phrases_topic:
                       flag = 0
                       for prev_phrase in final_phrases_topic:
                           similarity = sentence_similarity(nltk.word_tokenize(prev_phrase),
                                                            nltk.word_tokenize(phrase[1]),
                                                            stop_words)
                           if similarity > 0.99:
                               flag = 1
                               break
                       if not flag:
                           final_phrases_topic.append(phrase[1])
                   else:
                       final_phrases_topic.append(phrase[1])
       final_phrases.append(final_phrases_topic[:max_nodes])
   return final_phrases




def get_keywords(grouped_text, max_nodes=5):
   phrases_list = []
   for idx in grouped_text:
       if grouped_text[idx]:
           rake_model = Rake()
           rake_model.extract_keywords_from_text(grouped_text[idx])
           phrases = rake_model.get_ranked_phrases_with_scores()
           phrases_list.append(phrases)
       else:
           phrases_list.append([])
   final_keywords = get_best_phrases(phrases_list, max_nodes)
   common_list = get_common_phrases(phrases_list, max_nodes // 2)
   for phrase in common_list:
       keyword = phrase[0]
       if keyword not in final_keywords[phrase[1]]:
           final_keywords[phrase[1]].append(keyword)
       if keyword not in final_keywords[phrase[2]]:
           final_keywords[phrase[2]].append(keyword)
   return final_keywords




def create_keywords_from_text(text, max_nodes=5, sentence_group=3, num_topics=10):
   grouped_text, topics = create_topics(text, sentence_group, num_topics)
   keywords = get_keywords(grouped_text, max_nodes)
   return [keywords, topics]




def get_mindmap(keywords, topics):
   fig, ax = plt.subplots(figsize=(40, 25))
   G = nx.Graph()
   G.add_node("Mind Map")
   reg_exp_pattern = r"[^\d\w\s]"
   pastel_colors = ["#FFB6C1", "#ADD8E6", "#98FB98", "#FFD700", "#FFA07A", "#E6E6FA", "#FFDEAD"]
   shapes = ["o", "s", "D", "^", "v", "p", "h", "*"]
   shape_mapping = {"Mind Map": "o"}
   color_mapping = {"Mind Map": "#D3D3D3"}
   for idx, topic in topics.items():
       main_topic = re.sub(reg_exp_pattern, "", topic).strip()
       G.add_edge("Mind Map", main_topic)
       topic_color = np.random.choice(pastel_colors)
       topic_shape = np.random.choice(shapes)
       color_mapping[main_topic] = topic_color
       shape_mapping[main_topic] = topic_shape
       for keyword in keywords[idx]:
           keyword = re.sub(reg_exp_pattern, "", str(keyword)).strip()
           if keyword != main_topic:
               G.add_edge(main_topic, keyword)
               color_mapping[keyword] = topic_color
               shape_mapping[keyword] = topic_shape
   pos = nx.spring_layout(G, seed=42)
   for shape in set(shape_mapping.values()):
       node_list = [node for node in G.nodes if shape_mapping.get(node) == shape]
       node_colors = [color_mapping.get(node, "#D3D3D3") for node in node_list]
       if node_list:
           nx.draw_networkx_nodes(
               G, pos, nodelist=node_list, node_color=node_colors, node_shape=shape,
               node_size=2500, alpha=0.8
           )
   nx.draw_networkx_edges(G, pos, alpha=0.3, width=1.5)
   nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold", font_color="black")
   plt.title("Mind Map", fontsize=30, fontweight="bold")
   plt.close(fig)
   return fig




def load_text(file_name_path, encoding="utf8"):
   with open(file_name_path, encoding=encoding) as f:
       input_text = f.readlines()
   final_text = ''
   for text in input_text:
       final_text += text
   final_text = clean_text(final_text)
   return final_text





