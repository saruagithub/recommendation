# -*- coding:utf-8 -*-
# author:XueWang
import random
import math
import numpy as np
import pandas as pd
from operator import itemgetter

class ItemCF():
	def __init__(self):
		#similar 20 movie and recommend 10 for users
		self.n_similar_movie = 20
		self.n_recommend_movie = 10

		#dataset is divided into traindata and testdata
		self.traindata = pd.DataFrame(columns=['userId', 'movieId', 'rating', 'timestamp'])
		self.testdata = pd.DataFrame(columns=['userId', 'movieId', 'rating', 'timestamp'])

		#user similarity matrix
		self.movie_sim_matrix = {}
		self.movie_popular = {}
		self.movie_count = 0


	# 读文件得到“用户-电影”数据
	def load_file(self,filename):
		ratings = pd.read_csv(filename)
		#打乱数据
		shuffledata = ratings.sample(frac=1)
		self.traindata = shuffledata.iloc[0:int(shuffledata.shape[0]*0.75),]
		self.testdata = shuffledata.iloc[int(shuffledata.shape[0]*0.75):shuffledata.shape[0],]
		#print(self.testdata)


	# 计算电影之间的相似度
	def cal_movie_similarity(self):
		for movie in set(self.traindata['movieId'].values):
			self.movie_popular.setdefault(movie,0)
			self.movie_popular[movie] = self.traindata.loc[self.traindata['movieId'] == movie].shape[0]  #有多少行就有多少用户喜欢某电影

			for movie_other in set(self.traindata['movieId'].values):
				if movie == movie_other:
					continue
				self.movie_sim_matrix.setdefault(movie, {})
				self.movie_sim_matrix[movie].setdefault(movie_other, 0)
				# 统计同时看了movie和movie_other的用户有多少
				temp_table = self.traindata.loc[(self.traindata['movieId'] == movie) | (self.traindata['movieId'] == movie_other)]
				count = 0
				for k, v in temp_table['userId'].value_counts().items():
					if (v == 2):
						count = count + 1
				self.movie_sim_matrix[movie][movie_other] = count

		self.movie_count = len(self.movie_popular)
		print("Total movie number = %d" % self.movie_count)
		print("Build co-rated users matrix success!")

		# 计算电影之间的相似性
		for movie1,related_movies in self.movie_sim_matrix.items():
			for movie2, counts in related_movies.items():
				# 注意0向量的处理，即某电影的用户数为0
				if self.movie_popular[movie1] == 0 or self.movie_popular[movie2] == 0:
					self.movie_sim_matrix[movie1][movie2] = 0
				else:
					self.movie_sim_matrix[movie1][movie2] = counts / math.sqrt(self.movie_popular[movie1] * self.movie_popular[movie2])
		print('Calculate movie similarity matrix success!\n',self.movie_sim_matrix)


	# 针对目标用户U，找到K部相似的电影，并推荐其N部电影
	def recommend(self,user):
		K = self.n_similar_movie
		N = self.n_recommend_movie
		rank = {}
		watched_movies = self.traindata.loc[self.traindata['userId'] == user]
		for movie in watched_movies['movieId'].values:
			for related_movie, w in sorted(self.movie_sim_matrix[movie].items(),key=itemgetter(1),reverse=True)[:K]:
				if related_movie in watched_movies['movieId'].values:
					continue
				rank.setdefault(related_movie,0)
				rank[related_movie] += w * float(watched_movies.loc[watched_movies['movieId'] == movie]['rating'])
		return sorted(rank.items(),key=itemgetter(1),reverse=True)[:N]

	# 产生推荐并通过准确率、召回率和覆盖率进行评估
	def evaluate(self):
		N = self.n_recommend_movie
		#准确率和召回率
		hit = 0
		rec_count = 0
		test_count = 0
		#覆盖率
		all_rec_movies = set()


if __name__ == '__main__':
	rating_file = 'ml-latest-small/ratings.csv'
	itemCF = ItemCF()
	itemCF.load_file(rating_file)
	itemCF.cal_movie_similarity()
	#result  = itemCF.recommend(1)
	print(result)