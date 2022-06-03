# importing python package
import pandas as pd

# read contents of csv file
file = pd.read_csv("phrase_sent_test.csv")

# adding header
headerList = ['Sent', 'Phrase']

file = file[:200000]

# converting data frame to csv
file.to_csv("phrase_sent_test.csv", header=headerList, index=False)