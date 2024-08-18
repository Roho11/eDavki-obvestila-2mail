import requests
import pandas as pd
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime
from bs4 import BeautifulSoup
from config import SENDER_EMAIL, EMAIL_PASSWORD, RECEIVER_EMAIL

url = "https://edavki.durs.si/edavkiportal/openportal/commonpages/documents/ajax.aspx"

querystring = {"ng":"rss","url":"e_davki"}

payload = ""
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "sl-SI,sl;q=0.9,en-GB;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Cookie": "ASP.NET_SessionId=cuebejcym2v5wmhyuxnv4eko",
    "Referer": "https://edavki.durs.si/EdavkiPortal/OpenPortal/CommonPages/Opdynp/PageEdavkiRssView.aspx?rid=e_davki",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "^sec-ch-ua": "^\^Not/A",
    "sec-ch-ua-mobile": "?0",
    "^sec-ch-ua-platform": "^\^Windows^^^"
}

response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

response_json = response.json()

id_list = []
list_novic = []

for item in response_json['Items']:

    id = item['Id']
    naslov = item['Title']['Text']
    html_vsebina = item['Content']['Text']
    soup = BeautifulSoup(html_vsebina, "html.parser")
    vsebina = soup.text
    datum = item['PublishDate']
    #print(f'{id}: {naslov} \n {vsebina}')
    id_list.append(id)
    novica = {'id': id, 'naslov': naslov, 'vsebina': vsebina, 'datum': datum}
    list_novic.append(novica)
    
file_name = "obvestila.txt"

#Prebermo obstoječi seznam
with open(file_name, "r") as file:
    existing_ids = file.read()
existing_ids = existing_ids.split("\n")
existing_ids.pop(-1)

#dobimo samo tiste id-je katere moramo dodati v seznam in shraniti ter poslati mail
new_news = []
for novica in list_novic:
    if novica['id'] not in existing_ids:
        new_news.append(novica['id'])
        
for n in new_news:
    existing_ids.append(n)
    
#Shranimo posodobljen seznam
with open(file_name, "w") as file:
    for item in existing_ids:
        file.write(f"{item}\n")

df = pd.DataFrame(list_novic)
result_df = df.query('`id` in @new_news')

for index, row in result_df.iterrows():
    naslov = row['naslov']
    vsebina = row['vsebina']
    datum = row['datum']
    id = row['id']
    datum_obj = datetime.strptime(row['datum'], '%Y-%m-%dT%H:%M:%S%z')
    formatted_datum = datum_obj.strftime('%d.%m.%Y %H:%M')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400&display=swap');
            body {{
                font-family: 'Lato', sans-serif;
                background-color: #ffffff;
                margin: 0;
                padding: 0;
                color: #333333;
            }}
            .container {{
                padding: 20px;
                margin: 20px auto;
                max-width: 500px;
                border: 1px solid #dddddd;
            }}
            .header {{
                text-align: center;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            .content {{
                font-size: 16px;
                line-height: 1.6;
                margin-bottom: 20px;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #777777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{row['naslov']}</h1>
            </div>
            <div class="content">
                <p>{row['vsebina']}</p>
            </div>
            <div class="footer">
                <p>Objavljeno: {formatted_datum}</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = f'eDavki obvestilo: {id}'


    message.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
        print("Email sent successfully to", RECEIVER_EMAIL)
    except Exception as e:
        print("Email could not be sent:", str(e))
    finally:
        server.quit()
