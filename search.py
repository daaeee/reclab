import pandas as pd

data = pd.read_csv("C:/Users/МойПк/OneDrive/Рабочий стол/learning/SUM/Project/sait/short.csv", index_col=0)

# Sklearn

from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


name = []
stem = []
for i in range (36591):
    if data.iat[i,0] == "top250":
        name.append(data.iat[i,1])
        stem.append(data.iat[i,9])
df = pd.DataFrame({'name': name,'stem': stem})
df = df.groupby('name')['stem'].agg(' '.join).reset_index()

stem = []
for i in range (250):
    stem.append(df.iat[i,1])

name = '1+1 (2011)'
i = df.index [df['name']== name ]. tolist ()
print(type(i[0]))
find_nearest_to = df.iat[i[0], 1]

tfidf = TfidfVectorizer()
mx_tf = tfidf.fit_transform(stem)
new_entry = tfidf.transform([find_nearest_to])


# расчет косинусного расстояния
cosine_similarities = linear_kernel(new_entry, mx_tf).flatten()

#запишем все попарные результаты сравнений
df['cos_similarities'] = cosine_similarities

# и отсортируем по убыванию (т.к. cos(0) = 1)
df = df.sort_values(by=['cos_similarities'], ascending=[0])

mov = []
for i in range(4):
    mov.append(df.iat[i,0])
print(mov)
print(type(mov))