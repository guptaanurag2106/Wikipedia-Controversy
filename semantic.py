import difflib
import json
import os
import re

import mwparserfromhell
import nltk
import numpy as np
import textdistance
from sentence_transformers import SentenceTransformer, util

from LexRank import degree_centrality_scores

# model = SentenceTransformer('all-mpnet-base-v2')
model = SentenceTransformer('all-MiniLM-L6-v2')

articles_noncontroversial = []
for file in os.listdir("d:/IITD/OneDrive - IIT Delhi/IITD/SEM7/ELL880/project/api/noncontroversial_dataset"):
    if file.endswith(".json"):
        articles_noncontroversial.append("d:/IITD/OneDrive - IIT Delhi/IITD/SEM7/ELL880/project/api/noncontroversial_dataset/"+file)

articles_controversial = []
for file in os.listdir("d:/IITD/OneDrive - IIT Delhi/IITD/SEM7/ELL880/project/api/controversial_dataset"):
    if file.endswith(".json"):
        articles_controversial.append("d:/IITD/OneDrive - IIT Delhi/IITD/SEM7/ELL880/project/api/controversial_dataset/"+file)

def clean_wikipedia_content(content):
    wikicode = mwparserfromhell.parse(content)
    text = wikicode.strip_code()
    # Remove '\n' characters
    text = text.replace('\n', '').strip()
    # Remove multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def read_json_file(file_path):
    print('Reading file: ' + file_path)
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def find_revision(revisions, child_revision):
        for rev in revisions:
            if rev['revId'] == child_revision['parentId']:
                return rev
        return {}

def edit_extract_difflib(parent_content, child_content):
    differ = difflib.Differ()
    
    ins_edit_set = []
    del_edit_set = []
    mod_edit_set = []

    diffs = differ.compare(re.split(r'(?<=[.!?])\s+', parent_content),re.split(r'(?<=[.!?])\s+', child_content))
    for diff in diffs:
        if diff.startswith('+'):
            ins_edit_set.append(diff[2:])
        elif diff.startswith('-'):
            del_edit_set.append(diff[2:])
        elif diff.startswith('?'):
            mod_edit_set.append(diff[2:])


    return ins_edit_set, del_edit_set, mod_edit_set

def edit_extract(revisions):
    for revision in revisions:
        # jaccard = textdistance.Jaccard()
        # matched_sentences2 = {}
        parent_revision = find_revision(revisions, revision)
        if "content" not in parent_revision or "content" not in revision:
            revision['edit'] = ''
            continue
        parent_revision["content"] = clean_wikipedia_content(parent_revision["content"])
        revision["content"] = clean_wikipedia_content(revision["content"])
        parent_set = re.split(r'(?<=[.!?])\s+', parent_revision["content"])
        child_set = re.split(r'(?<=[.!?])\s+', revision["content"])

        edit = '. '.join([x for x in  child_set if x not in parent_set])
        edit1 = '. '.join([x for x in  parent_set if x not in child_set])

        # for sentence1 in parent_set:
        #     # print('a')
        #     for sentence2 in child_set:
        #         if sentence2 not in matched_sentences2:
        #             similarity = jaccard.similarity(sentence1, sentence2)
        #             if similarity >= 0.8:
        #                 matched_sentences2[sentence2] = True

        # difference = set(child_set) - set(matched_sentences2.keys())
        # edit = '. '.join(difference)
        revision["edit"] = edit
        revision["edit_delete"] = edit1
    return revisions


def calc_similarity(revisions):
    print('Calculating similarity', len(revisions))
    score = 0;
    a = 0;
    for revision in revisions:
        if "edit" not in revision:
            continue
        current_text = revision["edit"]
        parent_revision = find_revision(revisions, revision)
        # if not parent_revision:
        #     continue
        # if "edit" not in parent_revision:
        #     continue
        if "content" not in parent_revision:
            continue
        parent_text = parent_revision["content"]
        
        #Compute embedding for both lists
        embeddings1 = model.encode(current_text, convert_to_tensor=True)
        embeddings2 = model.encode(parent_text, convert_to_tensor=True)

        #Compute cosine-similarities
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        cosine_sim = cosine_scores[0][0]
        # print(cosine_sim)
        a += 1
        # score = 3*cosine_sim
        if cosine_sim < 0.5:
            score += 1
    print(a)
    if a == 0:
        return 0.5
    return score / a


a = 0
articles_noncontroversial = articles_noncontroversial[:8]
noncontroversial_similarity = []
for article in articles_noncontroversial:
    data = read_json_file(article)
    revisions = edit_extract(data)
    similarity_score = calc_similarity(revisions)
    a += similarity_score
    print(article, similarity_score)
    noncontroversial_similarity.append(similarity_score)
print('Non Controversial Average Similarity: ', a/len(articles_noncontroversial))

a = 0
articles_controversial = articles_controversial[:8]
controversial_similarity = []
for article in articles_controversial:
    data = read_json_file(article)
    revisions = edit_extract(data)
    similarity_score = calc_similarity(revisions)
    a += similarity_score
    print(article, similarity_score)
    controversial_similarity.append(similarity_score)
print('Controversial Average Similarity: ', a/len(articles_controversial))

print('Non Controversial Average Similarity: ', noncontroversial_similarity)
print('Controversial Average Similarity: ', controversial_similarity)
