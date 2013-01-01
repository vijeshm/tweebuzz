import networkx as nx
import tweepy as tw
import matplotlib.pyplot as plt
import time
import os
import random
import pickle
import re
import textwrap
from nltk.corpus import wordnet as wn
import string

def convertToDict(List):
	Dict = {}
	for Str in List:
		Dict[Str] = List.count(Str)
	return Dict

def plotHistogram(List, number):
	yaxis = [freq for freq,word in List[:number]]
	words = [word for freq,word in List[:number]]
	
	#yaxis = [freq for freq,word in List]
	#words = [word for freq,word in List]
	
	plt.plot(yaxis)
	for i in range(number):
		if i % 2 == 0:
			plt.text(i,0,words[i])
		else:
			plt.text(i,1,words[i])
	plt.show()

def removePunct(inputString):
	valid = string.letters + '0123456789@# '
	valid = [char for char in valid]
	outString = ""
	for char in inputString:
		if unicode(char) in valid:
			outString += char

	return outString
	
def removeSmileys(string, smileys):
	for smiley in smileys:
		string = string.replace(smiley, "")
		#string = re.sub(smiley, "", string)
	return string

def thesaurus(word, pos=None):
	allSyns = []
	for i, syn in enumerate(wn.synsets(word, pos)):
		syns = [n.replace('_', ' ') for n in syn.lemma_names]
		allSyns.extend(syns)

	allSyns = list(set(allSyns))
	if word in allSyns:
   		allSyns.remove(word)
	return allSyns

def getMentions(freq):
	mentions = {}
	for key in freq:
		if key.startswith('@'):
			mentions[key] = freq[key]

	for key in mentions:
		freq.pop(key)
	return mentions, freq

def getHashTags(freq):
	HashTags = {}
	for key in freq:
		if key.startswith('#'):
			HashTags[key] = freq[key]

	for key in HashTags:
		freq.pop(key)

	return HashTags, freq

def getLiveTweets(TL = False, numOfHomeTweets = 100, name = 'mvvijesh', numOfFriends = 15, topNlimit = 5, overWrite = False, fileName = "sampleTweets.txt"):
	consumer_key = 'rOpYjZTYVIYYTxh3TIw'
	consumer_secret = 'Cq5rT7Qqy7pmIMhEjWlgBUfdJYc68pTukSFbT57c4'
	auth = tw.OAuthHandler(consumer_key, consumer_secret)
	auth_url = auth.get_authorization_url()
	print 'Please Authorize: ' + auth_url
	os.system('chromium-browser ' + auth_url + ' &')
	verifier = raw_input('PIN: ').strip()
	auth.get_access_token(verifier)
	api = tw.API(auth)
	#print "ACCESS_KEY = '%s'" % auth.access_token.key
	#print "ACCESS_SECRET = '%s'" % auth.access_token.secret

	#timeInterval = 6
	#seconds = 20

	if not TL:
		topNtweets = {}
		friends = api.friends(name)
		print "processing... ",
		for twitterUser in random.sample(friends, numOfFriends):
			try:
				print " " + twitterUser.name,
				statuses = [tweet.text for tweet in twitterUser.timeline()]
				if len(statuses) >= topNlimit:
					topNtweets[twitterUser] = statuses[:topNlimit]
				else:
					topNtweets[twitterUser] = statuses
			except:
				print "Sorry, " + twitterUser.name + " has disabled the access."

		tweets = []
		for user in topNtweets:
			tweets.extend(topNtweets[user])

	else:
		tweets = [tweet.text for tweet in api.home_timeline(count = numOfHomeTweets)]


	if overWrite:
		Str = pickle.dumps(tweets)
		fptr = open(fileName,'w')
		fptr.write(Str)
		fptr.close()
		print "\nThe tweets have been saved to " + fileName
	
	return tweets

def getSavedTweets(fileName = "sampleTweets.txt"):
	fptr = open(fileName,'r')
	Str = fptr.read()
	fptr.close() 
	print "File Successfully read" 
	tweets = pickle.loads(Str)
	return tweets

def getWords(tweets, smileys):
	words = []
	for tweet in tweets:
		#print "Input:  ", tweet
		tweet = removeSmileys(tweet, smileys)
		#print "Middle: ", tweet
		tweet = removePunct(tweet)
		#print "Output: ", tweet
		#raw_input("Press return to continue..")
		#print ""

		words.extend(tweet.split())
	return words

def convertToLower(freq):
	for key in freq.keys():
		val = freq[key]
		freq.pop(key)
		freq[key.lower()] = val
	return freq

def removeCommon(freq, common):
	for commonWord in common:
		if freq.has_key(commonWord):
			freq.pop(commonWord)
	return freq

def addKeysAndThes(G, freq):
	for key in freq.keys():
		G.add_node(key)
	thes = thesaurus(key)

	for word in thes:
		G.add_edge(key, word)

def addTypeFrequencyScore(G, keys, freq):
	for node in G.nodes():
		if node in keys:
			G[node]['type'] = 'tweetWord'
			G[node]['freq'] = freq[node]
			G[node]['score'] = 0
		else:
			G[node]['type'] = 'thesWord'

def computeScores(G):
	for node in G.nodes():
		sumFreq = 0
		neighbors = G.neighbors(node)
		neighbors.remove('type')

		if G[node]['type'] == 'thesWord':
			for neighbor in neighbors:
				if G[neighbor]['type'] == 'tweetWord':
					sumFreq += G[neighbor]['freq']

			incCount = (sumFreq * (sumFreq - 1)) / 2

			for neighbor in neighbors:
				if G[neighbor]['type'] == 'tweetWord':
					G[neighbor]['score'] += incCount
		else:
			neighbors.remove('freq')
			neighbors.remove('score')

			for neighbor in neighbors:
				if G[neighbor]['type'] == 'tweetWord':
					G[node]['score'] += 1
					G[neighbor]['score'] += 1

def sortScores(G):
	scoreNode = []
	for node in G.nodes():
		if G[node]['type'] == 'tweetWord':
			scoreNode.append( (G[node]['score'], node) )
	scoreNode.sort(reverse = True)
	return scoreNode

def scoreUsingGraph(freq):
	G = nx.Graph()
	addKeysAndThes(G, freq)
	keys = freq.keys()
	addTypeFrequencyScore(G, keys, freq)
	computeScores(G)
	scoreNode = sortScores(G)
	return scoreNode

def scoreUsingSimpleThes(freq):
	scoreDict = {}
	for key in freq.keys():
		if not scoreDict.has_key(key):
			scoreDict[key] = 0

		for thesWord in thesaurus(key):
			if thesWord in freq.keys():
				if not scoreDict.has_key(thesWord):
					scoreDict[thesWord] = 0

				scoreDict[key] += (freq[key] + 1)
				scoreDict[thesWord] += freq[key]

	scorePair = [(score, word) for word, score in scoreDict.items()]
	scorePair.sort(reverse = True)
	e
	return scorePair

smileys = ['>:]', ':-\)', ':\)', ':o\)', ':]', ':3', ':c\)', ':>', '=]', '8\)', '=\)', ':}', ':^\)', '>:D', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D', '=-3', '=3', '8-\)', ':-\)', ':-\(', ':\(', ':-c', ':c', ':-<', ':<', ':-\[', ':\[', ':{', ':\*', ':-||', ':@', 'D:<', 'D:', 'D8', 'D;', 'D=', 'DX', 'v.v', 'D-', '>;]', ';-\)', ';\)', '\*-\)', '\*\)', ';-]', ';]', ';D', ';^\)', '>:P', ':-P', ':P', 'X-P', 'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:o', '>:O', ':-O', ':O', ':O', 'o_O', 'o_0', 'o.O', '8-0', '>:\\  ', '>:/ ', ':-/', ':-.', ':/', ':\\ ', '=/', '=\\ ', ':S', ':|', ':-|', '>:X', ':-X', ':X', ':-#', ':#', ':$', 'O:-\)', '0:-3', '0:3', 'O:-\)', 'O:\)', '0;^\)', '>:\)', '>;\)', '>:-\)', 'o/\o', '^5', '>_>^ ^<_<', '|;-\)', '|-O', '}:-\)', '}:\)', ';:-&', ':&', '#-\)', '%-\)', '%\)', ':-###..', ':###..', ':\'-\(', ':\'\(', ':\'-\)', ':\'\)', 'QQ', '<:-|', '<\*\)\)\)-{', '\*\0/\*', '@}-;-\'---', '@>-->--', '~\(_8^\(I\)', '5:-\)', '//0-0\\\\', '\*<|:-\)', '=:o]', ',:-\)', '7:^]']

#punctuations = ['\x83', '\x93', '\x97', '\x9b', '\x9f', '\xa3', '$', '\xa7', '(', '\xab', ',', '\xaf', '\xb3', '\xb7', '\xbb', '\xbf', '\xc3', '\\', '\xe3', '|', '\x80', '\x84', '\x88', '\x8c', '\x90', '\x94', '\x98', '\x9c', '\xa0', '\xa4', "\'", '\xa8', '\xac', '\/', '\xb0', '\xb4', '\xb8', ';', '?', '\xd8', '[', '_', '\xe0', '{', '\x81', '\x95', '\x99', '\x9d', '\xa1', '\"', '\xa5', '&', '\xa9', '*', '\xad', '.', '\xb1', '\xb5', '\xb9', ':', '\xbd', '^', '\xe1', '~', '\x82', '\t', '\x8a', '\x92', '\x96', '\x9e', '!', '\xa2', '%', '\xa6', ')', '\xaa', '-', '\xae', '\xb2', '\xb6', '\xba', '\xc2', '\xc6', ']', '\xe2', '}', '+']

common = ['a', 'about', 'after', 'again', 'air', 'all', 'along', 'also', 'an', 'and', 'another', 'any', 'are', 'around', 'as', 'ask', 'at', 'away', 'back', 'be', 'because', 'been', 'before', 'below', 'between', 'both', 'but', 'bring', 'broke', 'breaking', 'by', 'carry', 'came', 'can', 'check', 'come', 'could', 'day', 'did', 'didnt', 'different', 'drive', 'do', 'done', 'doing', 'does', 'dont', 'down', 'during', 'each', 'end', 'even', 'every', 'everyone', 'few', 'find', 'finds', 'first', 'for', 'found', 'from', 'get', 'gets', 'getting','give', 'go', 'going', 'got', 'good', 'gone', 'great', 'had', 'has', 'have', 'having', 'he', 'help', 'her', 'here', 'him', 'his', 'holding', 'home', 'house', 'how', 'i', 'im', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'join', 'joined', 'know', 'large', 'last', 'learned', 'left', 'like', 'line', 'little', 'long', 'look', 'lot', 'mark', 'made', 'make', 'makes', 'making', 'man', 'many', 'may', 'me', 'men', 'might', 'more', 'most', 'Mr.', 'must', 'my', 'name', 'need', 'never', 'new', 'next', 'no', 'not', 'now', 'number', 'of', 'off', 'old', 'on', 'one', 'only', 'or', 'other', 'our', 'out', 'over', 'own', 'part', 'people', 'place', 'put', 'read', 'right', 'route', 'said', 'same', 'saw', 'say', 'see', 'set', 'she', 'should', 'show', 'small', 'so', 'some', 'something', 'sound', 'still', 'start', 'such', 'take', 'taken', 'tell', 'than', 'that', 'the', 'them', 'then', 'there', 'these', 'they', 'thing', 'think', 'thanks', 'this', 'those', 'thought', 'three', 'through', 'time', 'to', 'today', 'together', 'too', 'top', 'try', 'two', 'u', 'under', 'up', 'ur', 'us', 'use', 'via', 'very', 'want', 'was', 'wasnt', 'water', 'way', 'we', 'well', 'went', 'were', 'what', 'whats', 'when', 'where', 'which', 'while', 'who', 'why', 'will', 'with', 'woah', 'word', 'work', 'working', 'run', 'world', 'would', 'wouldnt', 'write', 'yeah', 'year', 'yes', 'you', 'your', 'youve']

def main():
	tweetProps = [] #to maintain and deduce a list of properties for a particular tweets

	tweets = getLiveTweets(TL = True, numOfHomeTweets = 100, name = 'mvvijesh', numOfFriends = 15, topNlimit = 5, overWrite = True, fileName = "MyTimeLine.txt")
	tweets = getSavedTweets("MyTimeLine.txt")
	words = getWords(tweets, smileys)
	freq = convertToDict(words)
	freq = convertToLower(freq)
	freq = removeCommon(freq, common)

	mentions, freq = getMentions(freq)
	topMentions = [ (number,name) for name, number in mentions.items()]
	topMentions. sort(reverse = True)
	#print "mentions: ", [name for number, name in topMentions]

	hashtags, freq = getHashTags(freq)
	topHashTags = [ (number,hashtag) for hashtag, number in hashtags.items()]
	topHashTags. sort(reverse = True)
	#print "\n\nhashtags:", [hashTag for number, hashTag in topHashTags]

	#lTrend = scoreUsingGraph(freq)
	lTrend = scoreUsingSimpleThes(freq)
	
	print "Your top 20 local trends: "
	for word in lTrend[:20]:
		print word[1],

	print "\n\nYour top 20 Hot Mentions: "
	for name in topMentions[:20]:
		print name[1],

	print "\n\nYour top 20 Hot HashTags: "
	for name in topHashTags[:20]:
		print name[1],

main()