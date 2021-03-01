# NLTK PREPROCESSOR

# Preprocesses any string given to it using NLTK standard preprocessing tools

# IMPORT MODULES
import discord
import nltk

nltk.download('averaged_perceptron_tagger')

from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# VARIABLES
porterStemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# INIT
def initialize(al):
    
    # DEBUG
    print("> Initializing Module: Rosetta Processor v1")
    
    # DOWNLOAD REQUIRED MODULES
    nltk.download('punkt')
    
    # INIT VARIABLES
    global aliases
    aliases = al.copy()
    
def preprocessMessage(message):
    
    messageInfo = {
        "tokenized" : [],
        "tagged" : [],
        "final" : [], 
        "digits" : [],
        "mentions" : {},
        "quotes" : []
    }
    
    # -- TOKENISE --
    sents = sent_tokenize(message.clean_content.upper())

    tokenizedSents = [] 
    for sent in sents:
        tokenizedWords = word_tokenize(sent)
        tokenizedSents.append(tokenizedWords)
    
    
    # -- REMOVE ALIASES --
    cleanSents = []
    for sent in tokenizedSents:
        cleanWords = []
        for word in sent:
            
            for alias in aliases:
                if (alias in word or '@' in word):
                    break
            else:
                cleanWords.append(word)
        cleanSents.append(cleanWords)
    
    tokenizedSents = cleanSents
    messageInfo["tokenized"] = tokenizedSents
          
        
    # -- GROUP DISCORD CLASSES -- 
    mentionsDict = {
        "userMentions" : [], 
        "channelMentions" : []
    }
    
    # USER MENTIONS
    for mention in message.mentions:
        mentionsDict["userMentions"].append(mention)
        
    # CHANNEL MENTIONS
    for channelMention in message.channel_mentions:
        mentionsDict["channelMentions"].append(channelMention)
        
    messageInfo["mentions"] = mentionsDict
    
    
    # -- GROUP QUOTATIONS --
    quotes = []
    sentNo = 0
    while sentNo < len(sents):
        
        findNo = 0
        quoteStartNo = -1
        quoteEndNo = -1
        while findNo < len(sent):
            if (sent[findNo] == "``" or sent[findNo] == '"' or sent[findNo] == "'" or sent[findNo] == "''"):
                if (quoteStartNo == -1):
                    quoteStartNo = findNo
                else:
                    quoteEndNo = findNo
                    break
            
            findNo += 1
        
        # RECONSTRUCT QUOTE
        if (quoteStartNo != -1):
            quoteSentList = []
            
            quoteNo = quoteStartNo + 1
            while quoteNo < quoteEndNo:
                quoteSentList.append(sent[quoteNo])
                
                quoteNo += 1
            
            quote = {
                "quote" : " ".join(quoteSentList),
                "sentID" : sentNo
            }
            quotes.append(quote)
        
        sentNo += 1
            
    messageInfo["quotes"] = quotes
    
    
    # -- PART OF SPEECH TAGGING --
    taggedSents = []
    for sent in tokenizedSents:
        taggedSents.append(nltk.pos_tag(sent))
        
    messageInfo["tagged"] = taggedSents
    
    
    # -- LEMMATISING / STEMMING --
    def getWordnetPos(treebankTag):
        
        if (treebankTag.startswith("J")):
            return wordnet.ADJ
        elif (treebankTag.startswith("V")):
            return wordnet.VERB
        elif (treebankTag.startswith("N")):
            return wordnet.NOUN
        elif (treebankTag.startswith("R")):
            return wordnet.ADV
        else:
            return None
        
    lemmatisedSents = []
    for sent in taggedSents:
        
        lemmatisedWords = []
        for word in sent:
            
            wordnetPos = getWordnetPos(word[1])
            
            if not (wordnetPos == None):
                
                lemmatisedWords.append(
                    lemmatizer.lemmatize(word[0].lower(), wordnetPos).upper()
                )
                
            else:
                
                lemmatisedWords.append(
                    porterStemmer.stem(word[0]).upper()
                )
                
        lemmatisedSents.append(lemmatisedWords)
    
    # COMPILE FINAL TOGETHER LIST
    messageInfo["final"] = lemmatisedSents
    
    
    # -- SEPARATE PARTICULAR WORDS --
    for sent in messageInfo["tagged"]:
        
        if (sent == []):
            continue
        
        sentDigits = []
        
        for word in sent:
                
            # GROUP DIGITS
            if ("CD" in word[1]):
                sentDigits.append(word[0])
            
        messageInfo["digits"].append(sentDigits)
    
    
    return(messageInfo)