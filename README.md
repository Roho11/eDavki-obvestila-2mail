# eDavki-obvestila-2mail
Mail obvestilnik o delovanju spletnega portala eDavki

config.py >> mora imeti spremenljivke SENDER_EMAIL, EMAIL_PASSWORD, RECEIVER_EMAIL, ki se uporabljajo za argumente pošiljanja na mail

1. Prebere vsa obvestila iz https://edavki.durs.si/edavkiportal/openportal/commonpages/opdynp/pageedavkirssview.aspx?rid=e_davki (objavljenih je zadnjih 20)
2. V obvestila.txt zapiše ID novice, ki še ne obstajajo v datoteki
3. Pošlje HTML mail z naslovom, vsebino in datumom objave
