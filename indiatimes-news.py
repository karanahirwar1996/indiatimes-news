import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('wordnet')
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
def analyze_sentiment(text):
        sid = SentimentIntensityAnalyzer()
        sentiment_scores = sid.polarity_scores(text)
        return sentiment_scores['compound']*100
def calculate_positivity_score(positive_count, negative_count):
    total_count = positive_count + negative_count
    positivity_score = (positive_count-negative_count) / total_count*100 if total_count != 0 else 0
    return round(positivity_score,2)

def predict_stock_sentiment(sentence):
    words = word_tokenize(sentence.lower())
    
    positive_keywords = ["rise", "increase", "up", "bullish","growth","grow", "positive", "strong","Profit rises", "trimmed", "narrowed", "improved", "strengthening", "expand"]
    negative_keywords = ["fall", "decrease", "down", "bearish", "negative", "fell", "losses","slump","loss",
                         "lower", "dipped", "slowdown","plummeted","decline","plunges","Profit falls"]
    
    positive_count = 0
    negative_count = 0
    lemmatizer = WordNetLemmatizer()
    pos_list=[]
    neg_list=[]
    for p in positive_keywords:
            pos_list.append(lemmatizer.lemmatize(p, pos='v'))
    for n in negative_keywords:
            neg_list.append(lemmatizer.lemmatize(n, pos='v'))
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        if lemma in pos_list:
            positive_count += 1
        elif lemma in neg_list:
            negative_count += 1
    
    positivity_score = calculate_positivity_score(positive_count, negative_count)
    
    return positivity_score
  def india_times(page_count=5):
    import pandas as pd 
    import json
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    def extract_date(date_string):
        date_string = date_string.replace(" IST", "")
        datetime_obj = datetime.strptime(date_string, "%B %d, %Y, %I:%M %p")
        formatted_date = datetime_obj.strftime("%d/%m/%Y")
        return formatted_date
    def extract_time(date_string):
        date_string = date_string.replace(" IST", "")
        datetime_obj = datetime.strptime(date_string, "%B %d, %Y, %I:%M %p")
        formatted_date = datetime_obj.strftime("%I:%M %p")
        return formatted_date
    current_date = datetime.now().date()
    previous_date = current_date - timedelta(days=1)

    url = 'https://economictimes.indiatimes.com/markets/stocks/earnings/news'
    base_url = 'https://economictimes.indiatimes.com'
    tag = []
    href = []
    date=[]
    time=[]
    page = 1

    while page <= page_count:
        res = requests.get(url, params={'page': page})
        soup = BeautifulSoup(res.content, features="html.parser")

    # Check if there are no more articles
        if not soup.find_all("div", {"class": "eachStory"}):
            break

        for items in soup.find_all("div", {"class": "eachStory"}):
            tag.append(items.find("a").text)
            href.append(base_url + items.find('a')['href'])
            date.append(extract_date(items.find('time',{"class":"date-format"}).text))
            time.append(extract_time(items.find('time',{"class":"date-format"}).text))
        page += 1
    data = pd.DataFrame({'Headline': tag, 'URL': href,"date":date,"Time":time})
    data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
# Print the DataFrame
    filtered_df = data.loc[(data['date'] <= pd.to_datetime(current_date)) & (data['date'] >= pd.to_datetime(previous_date))]
    dip=[]
    for u in list(filtered_df["URL"]):
        res = requests.get(u)
        dip_soup = BeautifulSoup(res.content, features="html.parser")
        script_tag=dip_soup.find_all("script",{"type":"application/ld+json"})[1]
        script_data = script_tag.string.strip()
        data = json.loads(script_data)
        article_body = data.get("articleBody")
        dip.append(predict_stock_sentiment(article_body) if article_body else None)
    filtered_df["Deep Score"]=dip
    filtered_df['Normal Score']=filtered_df['Headline'].apply(analyze_sentiment)
    final=filtered_df.loc[(filtered_df['Deep Score']>45)&(filtered_df['Normal Score']>=0)].reset_index(drop=True)
    sender_email = "karan.ahirwar1996@gmail.com"
    receiver_email = ["anitaahirwar2112@gmail.com", sender_email]
    password = "uccrgtqdnusrpmnk"
    table_html = final.to_html(index=False)

    # Create the email message
    msg = MIMEMultipart()
    
    positive_news_count = len(final)
    msg["Subject"] = f"✨ Daily Positive News Digest-IndiaTimes - {current_date} ({positive_news_count} uplifting articles out of {len(filtered_df)})✨"
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_email)

    # HTML Template for the email content
    html_template = """
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        h1 {{
            color: #336699;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h1>Positive News - {current_date}</h1>
    {table}
</body>
</html>
"""


    # Set the message content with HTML template and table
    email_content = html_template.format(current_date=current_date, table=table_html)
    message = MIMEText(email_content, 'html')
    msg.attach(message)
    
    # Send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    return final
 india_times()
