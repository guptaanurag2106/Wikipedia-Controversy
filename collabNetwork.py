import json
import re
from difflib import SequenceMatcher
import networkx as nx
from datetime import datetime
import matplotlib.pyplot as plt
import mwparserfromhell
import csv
import numpy as np
import spacy

# Read JSON data from file
file_path = "Bruce_Castle.json"  # Replace with the actual path to your JSON file
article_title = re.sub(r'\.json', '', file_path).strip()
with open(file_path, "r") as file:
    rev_history = json.load(file)

# Clean Wikipedia Content
def clean_wikipedia_content(content):
    wikicode = mwparserfromhell.parse(content)
    text = wikicode.strip_code()
    # Remove '\n' characters
    text = text.replace('\n', '').strip()
    # Remove multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Function to split the text into sentences and words
# Load the spaCy English tokenizer
nlp = spacy.load("en_core_web_sm")

def tokenize_content(cleaned_content):
    doc = nlp(cleaned_content)
    words_per_sentence = [[(token.text, None) for token in sent] for sent in doc.sents]
    return words_per_sentence

# Function to calculate decision metric between two sentences
def LCS(old_sentence, new_sentence):
    words1 = [word for word, _ in old_sentence]
    words2 = [word for word, _ in new_sentence]
    
    seq_matcher = SequenceMatcher(None, words1, words2)
    match = seq_matcher.find_longest_match(0, len(words1), 0, len(words2))
    
    lcs_words = words1[match.a : match.a + match.size] if match.size > 0 else []
    lcs_old_indices, lcs_new_indices = [], []
    index_tracker = 0
    # Compute LCS Old Indices
    for word in lcs_words :
        for i in range(index_tracker, len(old_sentence)):
            if old_sentence[i][0] == word :
                lcs_old_indices.append(i)
                index_tracker = i + 1
                break
    # Compute LCS New Indices
    index_tracker = 0
    for word in lcs_words :
        for i in range(index_tracker, len(new_sentence)):
            if new_sentence[i][0] == word :
                lcs_new_indices.append(i)
                index_tracker = i + 1
                break
    if len(lcs_new_indices) != len(lcs_old_indices) :
        print("teri maki chut")
    return len(lcs_words)/len(old_sentence), lcs_old_indices, lcs_new_indices

# Sort revisions by timestamp using datetime parsing
sorted_revisions = sorted(rev_history, key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%dT%H:%M:%SZ"))

# Create a directed graph
G = nx.DiGraph()

# Store the previous content structure
prev_content_structure = []

# Iterate over sorted revisions and retrieve the content of each revision
for i, revision in enumerate(sorted_revisions):
    # Status Update
    print(f"Processing Revision [{i+1}/{len(sorted_revisions)}]")
    # Obtain Cleaned Content
    curr_content = clean_wikipedia_content(revision.get("content", ""))
    curr_author = revision.get("user", None)
    curr_authorhsip = 0
    # Dictionary to store word counts per author
    deleted_word_counts = {}
    # Add Node to the graph
    if not G.has_node(curr_author):
        G.add_node(curr_author, authorship = None)
    # Break content into an unordered set of sentences
    curr_content_structure = tokenize_content(curr_content)
    # Sentence Matching 
    if i == 0 :
        curr_content_structure=[[(word, curr_author) for (word, _) in sentence] for sentence in curr_content_structure]
        G.nodes[curr_author]['authorship'] = sum(len(sentence) for sentence in curr_content_structure)
    else:
        # Sentence Matching
        match_dict = {}
        deleted_sentence_indices = []
        for old_ind, old_sentence in enumerate(prev_content_structure):
            metric_max_index = -1
            metric_max_value = 0
            for new_ind, new_sentence in enumerate(curr_content_structure):
                if new_ind in match_dict.keys():
                    continue
                metric, _, _ = LCS(old_sentence, new_sentence)
                if metric > metric_max_value:
                    metric_max_value = metric
                    metric_max_index = new_ind
            if metric_max_index != -1 :
                match_dict[metric_max_index] = old_ind
        # Deleted Sentences
        for old_ind, old_sentence in enumerate(prev_content_structure):
            if old_ind in match_dict.keys():
                continue
            for word, author in old_sentence :
                if author not in deleted_word_counts :
                    deleted_word_counts[author] = 0
                deleted_word_counts[author] += 1 
        # New Strcuture formation
        for sentence_ind, sentence in enumerate(curr_content_structure) :
            if sentence_ind in match_dict.keys() :
                _, lcs_old_indices, lcs_new_indices = LCS(prev_content_structure[match_dict[sentence_ind]], sentence)
                for word_ind, (word, _) in enumerate(curr_content_structure[sentence_ind]) :
                    if word_ind in lcs_new_indices :
                        curr_content_structure[sentence_ind][word_ind] = (word, prev_content_structure[match_dict[sentence_ind]][lcs_old_indices[lcs_new_indices.index(word_ind)]][1])
                    else :
                        curr_content_structure[sentence_ind][word_ind] = (word, curr_author)
                for word_ind, (word, author) in enumerate(prev_content_structure[match_dict[sentence_ind]]) :
                    if word_ind in lcs_old_indices :
                        continue
                    if author not in deleted_word_counts :
                        deleted_word_counts[author] = 0
                    deleted_word_counts[author] += 1
            else:
                curr_content_structure[sentence_ind] = [(word, curr_author) for (word, _) in sentence]
        # Update Node Authorship
        for sentence in curr_content_structure :
            for word, author in sentence :
                if author == curr_author :
                    curr_authorhsip += 1
        G.nodes[curr_author]["authorship"] = curr_authorhsip
        # Update Edges
        author_u = curr_author
        for author_v in deleted_word_counts.keys() :
            if G.has_edge(author_u, author_v):
                G[author_u][author_v]['weight'] += deleted_word_counts[author_v]
            else :
                G.add_edge(author_u, author_v, weight = deleted_word_counts[author_v])
    # Update Previous Content Strcuture
    prev_content_structure = curr_content_structure

# Plot the graph
pos = nx.kamada_kawai_layout(G)  # You can use different layout algorithms
nx.draw(G, pos, with_labels=False, font_weight='bold', node_color='skyblue', font_size=8, node_size=10, arrowsize=8)
plt.title("Edit Network Graph")
plt.show()

# Save the graph structure in CSV format
csv_file_path = f"{article_title}_graph_structure.csv"  # Replace with the desired file path
with open(csv_file_path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)

    # Write header row
    csv_writer.writerow(["Source", "Target", "Weight"])  # Adjust column names as needed

    # Write edges and weights
    for edge in G.edges(data=True):
        source, target, data = edge
        weight = data.get("weight", 1)  # Assuming the default weight is 1 if not specified
        csv_writer.writerow([source, target, weight])

def bipolarity(G) :
    # Create the adjacency matrix A
    A = nx.adjacency_matrix(G).todense()
    # Calculate the eigenvalues
    eigenvalues = np.linalg.eigvals(A)
    # Find the minimum and maximum eigenvalues
    lambda_min = min(eigenvalues)
    lambda_max = max(eigenvalues)
    # Calculate bipolarity
    bipolarity = -lambda_min / lambda_max
    # Return real part of bipolarity
    return np.real(bipolarity)

# Print the Bipolarity for Edit Network G of article with title Artcicle_title
print(f"Bipolarity for Edit Network of article with title {article_title} : {bipolarity(G)}")



