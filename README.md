# Wikipedia-Controversy

## Overview
This project explores controversy detection within Wikipedia articles using collaboration networks and semantic similarity analysis. Leveraging data obtained from the Wikipedia API, it delves into a comprehensive study of article revision histories (500 revisions per article) to identify and analyze controversies.

### Data Collection
The article revision histories were fetched using the Wikipedia API (code located in the `api` folder). For this analysis, 500 revisions of each article were considered, providing a robust dataset for investigation.

### Ground Truth Labels
To establish ground truth labels for controversial and non-controversial articles, the project utilizes Wikipedia's curated lists of [controversial](https://en.wikipedia.org/wiki/Wikipedia:List_of_controversial_issues) and [featured articles](https://en.wikipedia.org/wiki/Wikipedia:Featured_articles). These lists serve as reference lables for evaluating the controversy detection methodology.

### Methodology
The methodology for controversy detection is based on a combination of collaboration network analysis and semantic dissimilarity.

### Results
- Collaboration networks:
  ```
  Precision: 69.23%
  Recall: 85.71%
  F1 Score: 76.60%
  ```
- Semantic Dissimilarity:
  The model did not perform very well and got a Precision of about 56%

### Article Dataset
The dataset comprising article revision histories (500 revisions each) is hosted on Google Drive. Access the dataset [here](insert_google_drive_link).

## Repository Structure
- `/api`: Contains code for interacting with the Wikipedia API and fetching article revision histories.
- `collabNetworks.py`: Contains code for generating edit networks and calculating biploarity
- `semantic.py`: Contains code for analyzing temporal semantic changes using [sentence transformers](https://www.sbert.net/)

## Usage
- Clone the repository: `git clone https://github.com/guptaanurag2106/Wikipedia-Controversy.git`
- ```bash
  cd api
  node script.js
  ```

## References
 The following academic papers serve as foundational references for this approach:

- Hoda Sepehri Rad and Denilson Barbosa. 2012. Identifying controversial articles in Wikipedia: a comparative study. In Proceedings of the Eighth Annual International Symposium on Wikis and Open Collaboration (WikiSym '12). Association for Computing Machinery, New York, NY, USA, Article 7, 1–10. https://doi.org/10.1145/2462932.2462942
- Ulrik Brandes, Patrick Kenis, Jürgen Lerner, and Denise van Raaij. 2009. Network analysis of collaboration structure in Wikipedia. In Proceedings of the 18th international conference on World wide web (WWW '09). Association for Computing Machinery, New York, NY, USA, 731–740. https://doi.org/10.1145/1526709.1526808
- M. Zeeshan Jhandir, Ali Tenvir, Byung-Won On, Ingyu Lee, and Gyu Sang Choi. 2017. Controversy detection in Wikipedia using semantic dissimilarity. Inf. Sci. 418, C (December 2017), 581–600. https://doi.org/10.1016/j.ins.2017.08.037
