# -*- coding:utf-8 -*-
# author:XueWang
import pandas as pd
import numpy as np

def main():
	#read MovieLens 1M data
	users = pd.read_table('ml-1m/'+'users.dat',sep = '::', names = ['UserID','Gender','Age','Occupation','Zip-code'],engine='python')
	ratings = pd.read_table('ml-1m/'+'ratings.dat',sep = '::', names = ['UserID','MovieID','Rating','Timestamp'],engine='python')
	movies = pd.read_table('ml-1m/'+'movies.dat',sep = '::',names=['MovieID','Title','Genres'],engine='python')
	#a = ratings.loc[ratings['UserID'] == 2].shape[0]

	#ratings = pd.read_excel('ml-1m/'+'rating1.xlsx')
	#print(ratings)
	movies_length = movies.shape[0]
	users_length = users.shape[0]
	for i in range(movies_length):
		if(movies.at[i,'MovieID'] != i+1):
			old = movies.at[i, 'MovieID']
			for j in range(ratings.shape[0]):
				if(ratings.at[j,'MovieID'] == old):
					ratings.at[j, 'MovieID'] = i+1
			movies.at[i, 'MovieID'] = i+1

if __name__ == '__main__':
	main()