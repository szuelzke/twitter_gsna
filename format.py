#convert txt file to csv file

# importing panda library 
import pandas as pd 
  
# readinag given csv file 
# and creating dataframe 
dataframe1 = pd.read_csv("twitter_combined_copy.txt") 
  
# storing this dataframe in a csv file 
dataframe1.to_csv('twitter_combined.csv',  
                  index = None) 