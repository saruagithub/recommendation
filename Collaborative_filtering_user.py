# -*- coding:utf-8 -*-
# author:XueWang
import pandas as pd
import numpy as np
import xlrd

def UserSimilarity(ratings,movies_length,users_length):
	# build inverse table for item_users
	movie_users = [] # MovieId starts from 1
	for i in range(1,movies_length+1):
		temp_ratings = ratings.loc[ratings['MovieID'] == i] #计算每个电影对应哪些用户
		if temp_ratings.shape[0] == 0: #电影i没有一个 人评分
			movie_users.append([0])
		else:
			movie_users.append(temp_ratings['UserID'].values)

	# calculate co-rated items between users
	user_user = np.zeros([users_length,users_length])
	N_user = np.zeros([1,users_length])
	for i in range(movies_length):
		for user in movie_users[i]:
			N_user[0,user-1] = N_user[0,user-1] + 1 #userID starts from 1
			for otheruser in movie_users[i]:
				if(user != otheruser):
					user_user[user-1,otheruser-1] = user_user[user-1,otheruser-1] + 1 #此处可优化，存半矩阵

	# calculate finial similarity matrix W
	print(np.dot(N_user.transpose(),N_user))
	similarity_W = user_user / np.sqrt(np.dot(N_user.transpose(),N_user))
	#where_are_nan = np.isnan(similarity_W)
	#similarity_W[where_are_nan] = 0
	return similarity_W,movie_users

def Recommend(ratings,movie_users,similarity_W):
	#UserCF推荐算法，K取3，rvi为评分
	K = 3
	similarity_Kuser = [[0 for i in range(K)] for j in range(similarity_W.shape[0])]
	for u in range(similarity_W.shape[0]):
		temp_similarW = similarity_W[u].copy() #注意深拷贝和浅拷贝
		for k in range(K):
			max_index = np.argmax(temp_similarW)
			similarity_Kuser[u][k] = max_index+1 #userID
			temp_similarW[max_index] = 0.0 #方便计算下一个最大的相似用户

	p_recommend = pd.DataFrame(columns=['UserID', 'MovieID', 'p_value'])
	for u in range(similarity_W.shape[0]):
		movies = [0 for i in range(K)]
		mine = ratings.loc[ratings['UserID'] == u+1]
		own_movies = mine['MovieID'].values.tolist()
		for k in range(K):
			kuser_movies = ratings.loc[ratings['UserID']==similarity_Kuser[u][k]]
			movies[k] = kuser_movies['MovieID'].values.tolist()
		new_movies = set(movies[0] + movies[1] + movies[2]).difference(set(own_movies))

		for movie in new_movies: #calculate the p(u,i)
			p = 0.0
			for user in movie_users[movie-1]:
				if user in similarity_Kuser[u]:
					rate = ratings[(ratings['UserID']==user) & (ratings['MovieID']==movie)]
					p = list(similarity_W[u][user-1] * rate['Rating'])[0] + p
			p_recommend = p_recommend.append(pd.DataFrame({'UserID':[u+1], 'MovieID':[movie], 'p_value':[p]}),ignore_index=True)
	#p_recommend.sort_values('p_value', inplace=True)
	return p_recommend


def main():
	#read MovieLens 1M data
	users = pd.read_table('ml-1m/'+'users.dat',sep = '::', names = ['UserID','Gender','Age','Occupation','Zip-code'],engine='python')
	ratings = pd.read_table('ml-1m/'+'ratings.dat',sep = '::', names = ['UserID','MovieID','Rating','Timestamp'],engine='python')
	movies = pd.read_table('ml-1m/'+'movies.dat',sep = '::',names=['MovieID','Title','Genres'],engine='python')
	movies_length = movies.shape[0]
	users_length = users.shape[0]

	# another data rating1.xlsx
	#ratings = pd.read_excel('ml-1m/'+'rating1.xlsx')
	#print(ratings)
	#movies_length = 20
	#users_length = 5

	#data preprocessing MovieID from 1 to N
	for i in range(movies_length):
		if(movies.at[i,'MovieID'] != i+1):
			old = movies.at[i, 'MovieID']
			for j in range(ratings.shape[0]):
				if(ratings.at[j,'MovieID'] == old):
					ratings.at[j, 'MovieID'] = i+1
			movies.at[i, 'MovieID'] = i+1

	#calculate user similarity
	similarity_W,movie_users = UserSimilarity(ratings,movies_length,users_length)#可优化，rating中评分＞3的才是用户喜欢的电影
	# recommend score
	recommend = Recommend(ratings,movie_users,similarity_W)
	print(recommend)
	#finally you can sort it and get the top N

if __name__ == '__main__':
	main()