"""
@author: 成昊
@desc: 对 dataframe 进行分词处理, 生成 tfidf 模型用于匹配
"""
import sys
import pickle
import numpy as np
from config import *
from tokenizer import MatchTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer


def max_pooling(tfidf, title_idx, title_count):
    words_dim = tfidf.shape[1]
    result = []
    for _ in range(title_count):
        result.append(np.zeros((1, words_dim)))

    for i in range(tfidf.shape[0]):
        idx = title_idx[i]
        result[idx] = np.max([result[idx], tfidf[i, :].toarray()], axis=0)
    return result


def text2tfidf(text):
    tv = TfidfVectorizer()
    tfidf = tv.fit_transform(text)
    return tfidf, tv


def run():
    print('Preprocess start')
    with open(DATA_PATH, 'rb') as data_file:
        jds = pickle.load(data_file)
    jds = jds[['职位描述', 'standard_title']]
    print('JD data loaded')

    print('Cutting sentence...')
    tokenizer = MatchTokenizer()
    cut_jd = []

    for idx, row in jds.iterrows():
        cut = tokenizer.cut(row['职位描述'])
        cut_jd.append(' '.join(cut))
        if idx % 1000 == 0 or idx == len(jds)-1:
            sys.stdout.write('\rProcessing %.2f%%' % ((idx+1)/len(jds)))
            sys.stdout.flush()
    del jds['职位描述']
    print('Done!')

    print('Converting to TF-IDF...')
    tfidf, tv = text2tfidf(cut_jd)
    print('Done')

    print('Max pooling...')
    title2idx = {val: idx for idx, val in enumerate(jds['standard_title'])}
    idx2title = {idx: val for idx, val in enumerate(jds['standard_title'])}
    title_idx = [title2idx[title] for title in jds['standard_title']]
    tfidf = max_pooling(tfidf, title_idx, len(title2idx))
    print('Done')

    print('Saving result...')
    with open(TITLE2IDX_PATH, 'wb') as f:
        pickle.dump(title2idx, f)
    with open(IDX2TITLE_PATH, 'wb') as f:
        pickle.dump(idx2title, f)
    with open(TFIDF_PATH, 'wb') as f:
        pickle.dump(tfidf, f)
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump(tv, f)
    print('All done!')


if __name__ == '__main__':
    run()
