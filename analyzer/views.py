from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pandas as pd
from textblob import TextBlob
from matplotlib import pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import pandas as pd  ### For reading the csv file
import numpy as np  ##### For joins the different array
import pickle  #### For Saving the svm model
from sklearn.feature_extraction.text import TfidfVectorizer  ### For converting numeric value
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier

# Create your views here.
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')

        context = {'form': form}
        return render(request, 'register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    return render(request, 'index.html')


count = 0
strg = ""
@login_required(login_url='login')
def predict1(request):
    global count
    global strg
    count = 0
    strg = ""

    input_text = request.POST.get("fulltextarea", "").strip()
    if not input_text:
        messages.error(request, "Input text cannot be empty.")
        return redirect('home')

    import requests
    import pandas as pd
    from bs4 import BeautifulSoup
    import numpy as np
    import re
    from nltk import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from sklearn.feature_extraction.text import TfidfVectorizer
    import pickle

    is_url = input_text.startswith("http://") or input_text.startswith("https://")

    if is_url:
        url = input_text
        HEADERS = ({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

        try:
            req = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(req.content, 'lxml')
        except Exception as e:
            messages.error(request, f"Failed to fetch the URL: {str(e)}")
            return redirect('home')

        # check = 1
        if "amazon" in url:
            check = 1
            print("Amazon")
            url = url.replace("/dp/", "/product-reviews/")
            url = url.replace("arp_d_product_top", "dp_d_show_all_btm")
            url += "reviewerType=all_reviews&pageNumber=0"
            print(url)
        else:
            check = 2
            url = url.replace("/p/", "/product-reviews/")
            url += "&page=1"
            print(url)

        def fun(url, i):
            global count
            global flag
            if count > 7:
                flag = 0
                return

            try:
                req = requests.get(url, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(req.content, 'lxml')
            except Exception:
                return

            global strg

            if check == 1:
                if (soup.find_all('div', class_="a-row a-spacing-small review-data")):
                    count = 0
                    print("Extracting Reviews from Page", str(i) + "...")
                    for item in soup.find_all('div', class_="a-row a-spacing-small review-data"):
                        strg = strg + item.text + "\n"
                        print(strg)
            else:
                if (soup.find_all('div', class_="t-ZTKy")):
                    count = 0
                    print("Extracting Reviews from Page", str(i) + "...")
                    for item in soup.find_all('div', class_="t-ZTKy"):
                        strg += item.text + "\n"
                        print(strg)
                else:
                    flag = 0
                    return

        flag = 1
        for x in range(1, 3):
            url = url[:-1] + str(x)
            fun(url, x)
        strg1 = strg.replace("READ MORE", ".")
    else:
        strg1 = input_text

    if is_url and not strg1.strip():
        messages.error(request, "Failed to scrape reviews from the provided URL. The website might be blocking automated requests or the page does not contain reviews. Try copying and pasting the reviews text directly into the text box instead.")
        return redirect('home')

    def remove_emojis(data):
        emoj = re.compile("["
                          u"\U0001F600-\U0001F64F"  # emoticons
                          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                          u"\U0001F680-\U0001F6FF"  # transport & map symbols
                          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                          u"\U00002500-\U00002BEF"  # chinese char
                          u"\U00002702-\U000027B0"
                          u"\U00002702-\U000027B0"
                          u"\U000024C2-\U0001F251"
                          u"\U0001f926-\U0001f937"
                          u"\U00010000-\U0010ffff"
                          u"\u2640-\u2642"
                          u"\u2600-\u2B55"
                          u"\u200d"
                          u"\u23cf"
                          u"\u23e9"
                          u"\u231a"
                          u"\ufe0f"  # dingbats
                          u"\u3030"
                          "]+", re.UNICODE)
        return re.sub(emoj, '', data)

    clean_text = (remove_emojis(strg1))  # no emoji

    stopWords = set(stopwords.words("english"))  ### define stopwords
    words = word_tokenize(clean_text)  ### tokanization

    freqTable = dict()
    for word in words:
        word = word.lower()  ### converting upper to lower case
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    sentences = sent_tokenize(clean_text)  ### separate sentence to words
    sentenceValue = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq

    if not sentenceValue:
        messages.error(request, "No sentences could be evaluated. Try entering a longer text with more words.")
        return redirect('home')

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]
    # Average value of a sentence from the original text
    average = int(sumValues / len(sentenceValue))
    # Storing sentences into our summary.
    summary = ''
    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.9 * average)):
            summary += " " + sentence

    if not summary.strip():
        sorted_sentences = sorted(sentenceValue.items(), key=lambda x: x[1], reverse=True)
        if sorted_sentences:
            summary = sorted_sentences[0][0]
        else:
            summary = clean_text[:200]

    d = [summary]
    data = pd.read_csv("reviews_dataset.csv")

    train_corpus = data['summarization']
    tf = TfidfVectorizer()
    tf.fit_transform(train_corpus)
    test_tfidf = tf.transform(d)
    
    with open('random_forest_model.sav', 'rb') as f:
        loaded_model = pickle.load(f)

    test_tfidf1 = test_tfidf.toarray()
    test_tfidf2 = np.c_[test_tfidf1]
    abc = loaded_model.predict(test_tfidf2)
    print(abc)
    context = {
        "given_review1": summary,
        "review": abc[0]
    }

    return render(request, 'result.html', context)















