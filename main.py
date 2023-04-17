import re
from flask import Flask, jsonify
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import feedparser
from classs import news

pd.set_option('display.max_colwidth', 500)
api_key = "AIzaSyAKY_4kNJ0xHBgVCE6k9ZgSX-njXno1BTQ"
API_URL = "https://api-inference.huggingface.co/models/CAMeL-Lab/bert-base-arabic-camelbert-msa-ner"
headers = {"Authorization": "Bearer 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"}

app = Flask(__name__)


@app.route('/')
def index():
    def extract(important_list):
        for newsObjectData in important_list:

            url = newsObjectData.GetLink()  # get the objects link (the news link)

            response = requests.get(url)  # request the page
            soup = BeautifulSoup(response.content, "html.parser")  # open the page

            # find all sections in the HTML
            sections = soup.find_all("section")

            # check if there are at least four sections
            if len(sections) >= 4:
                target_section = sections[4]
                target_section_contents = target_section.get_text()
                target_section_contents = "\n".join(
                    [line.strip() for line in target_section_contents.split("\n") if "اقرأ أيضاً" not in line.strip()])
                target_section_contents = re.sub(r'\n{2,}', '\n', target_section_contents)
                target_section_contents = re.sub(r',','',target_section_contents)
                newsObjectData.Setdescription(target_section_contents)  # sets the description of the news object

        ExtractLocation(important_list)  # calls the extract location to extract the location from the description

    def extract_static(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # find all sections in the HTML
        sections = soup.find_all("div", {"class": "article"})

        # check if there are at least two sections

        for data in sections:
            second_section_contents = data.get_text()
            second_section_contents = "\n".join(
                [line.strip() for line in second_section_contents.split("\n") if line.strip()])

    def get_boundary_coordinates(place_name):
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place_name}&key={api_key}"
        response = requests.get(geocode_url)
        response_json = response.json()
        results = response_json["results"]
        if len(results) == 0:
            return None
        result = results[0]
        geometry = result["geometry"]
        bounds = geometry.get("bounds")
        if bounds is None:
            viewport = geometry["viewport"]
            southwest = viewport["southwest"]
            northeast = viewport["northeast"]
            boundary_coordinates = [(southwest["lat"], southwest["lng"]), (northeast["lat"], northeast["lng"])]
        else:
            southwest = bounds["southwest"]
            northeast = bounds["northeast"]
            boundary_coordinates = [(southwest["lat"], southwest["lng"]), (northeast["lat"], northeast["lng"]),
                                    (northeast["lat"], southwest["lng"]), (southwest["lat"], northeast["lng"])]
        return boundary_coordinates

    def GetDataAndDescription(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        estimatedTime = 0.0
        if 'estimated_time' in response.json():
            estimatedTime = response['estimated_time']
            print(estimatedTime)
        else:
            print("No est")
            print(response.json())

        if estimatedTime > 0:
            time.sleep(estimatedTime)
            response = requests.post(API_URL, headers=headers, json=payload)

        return response.json()

    def ExtractLocation(important_list):
        theLocation = ""
        countryList=["أفغانستان",
  "الجزائر",
  "البحرين",
  "بنغلاديش",
  "بوتان",
  "البرازيل",
  "بروناي",
  "بلغاريا",
  "بوركينا فاسو",
  "بوروندي",
  "كمبوديا",
  "الكاميرون",
  "الرأس الأخضر",
  "جمهورية أفريقيا الوسطى",
  "تشاد",
  "الصين",
  "كولومبيا",
  "جزر القمر",
  "جمهورية الكونغو",
  "جمهورية الكونغو الديمقراطية",
  "كوستاريكا",
  "كوت ديفوار",
  "كرواتيا",
  "كوبا",
  "قبرص",
  "التشيك",
  "الدنمارك",
  "جيبوتي",
  "دومينيكا",
  "جمهورية الدومينيكان",
  "تيمور الشرقية",
  "الإكوادور",
  "مصر",
  "السلفادور",
  "غينيا الإستوائية",
  "إريتريا",
  "إستونيا",
  "إثيوبيا",
  "فيجي",
  "فنلندا",
  "فرنسا",
  "الغابون",
  "غامبيا",
  "جورجيا",
  "ألمانيا",
  "غانا",
  "اليونان",
  "غرينادا",
  "غواتيمالا",
  "غينيا",
  "غينيا-بيساو",
  "غيانا",
  "هايتي",
  "هندوراس",
  "المجر",
  "آيسلندا",
  "الهند",
  "إندونيسيا",
  "إيران",
  "العراق",
  "جمهورية أيرلندا",
  "إسرائيل",
  "إيطاليا",
  "جامايكا",
  "اليابان",
  "الأردن",
  "كازاخستان",
  "كينيا",
  "كيريباتي",
  "كوريا الشمالية",
  "كوريا الجنوبية",
  "الكويت",
  "قرغيزستان",
  "لاوس",
  "لاتفيا",
  "لبنان",
  "ليسوتو",
  "ليبيريا",
  "ليبيا","ليختنشتاين",
"ليتوانيا",
"لوكسمبورغ",
"مدغشقر",
"مالاوي",
"ماليزيا",
"جزر المالديف",
"مالي",
"مالطا",
"جزر مارشال",
"موريتانيا",
"موريشيوس",
"المكسيك",
"مايكرونيزيا",
"مولدوفا",
"موناكو",
"منغوليا",
"الجبل الأسود",
"المغرب",
"موزمبيق",
"ميانمار",
"ناميبيا",
"ناورو",
"نيبال",
"هولندا",
"نيوزيلندا",
"نيكاراجوا",
"النيجر",
"نيجيريا",
"جزيرة النورفولك",
"مقدونيا الشمالية",
"النرويج",
"عمان",
"باكستان",
"بالاو",
"بنما",
"بابوا غينيا الجديدة",
"باراغواي",
"بيرو",
"الفلبين",
"بولندا",
"البرتغال",
"قطر",
"رومانيا",
"روسيا",
"رواندا",
"سانت كيتس ونيفيس",
"سانت لوسيا",
"سانت فينسنت والغرينادين",
"ساموا",
"سان مارينو",
"ساو تومي وبرينسيبي",
"المملكة العربية السعودية",
"السنغال",
"صربيا",
"سيشل",
"سيراليون",
"سنغافورة",
"سلوفاكيا",
"سلوفينيا",
"جزر سليمان",
"الصومال",
"جنوب إفريقيا",
"جنوب السودان",
"إسبانيا",
"سريلانكا",
"السودان",
"سورينام",
"سوازيلاند",
"السويد",
"سويسرا",
"سوريا",
"تايوان",
"طاجيكستان",
"تنزانيا",
"تايلاند",
"توغو",
"تونجا",
"ترينداد وتوباغو","تركيا",
"تركمانستان",
"توفالو",
"أوغندا",
"أوكرانيا",
"الإمارات العربية المتحدة",
"المملكة المتحدة",
"الولايات المتحدة الأمريكية",
"أوروغواي",
"أوزبكستان",
"فانواتو",
"فنزويلا",
"فيتنام",
"اليمن",
"زامبيا",
"زيمبابوي",
"أمريكا"]
        provinces=["عجلون",
  "العقبة",
  "الزرقاء",
  "السلط",
  "جرش",
  "الكرك",
  "معان",
  "المفرق",
  "مادبا",
  "عمان",
  "الطفيلة",
  "إربد"]
        for newsData in important_list:
            if newsData.Getdescription() != '':  # check if there is a description
                response = GetDataAndDescription(newsData.Getdescription())  # send the description to the function

                for item in response:
                    if isinstance(item, dict) and 'entity_group' in item:
                        if item['entity_group'] == 'LOC':
                            if item['word'] not in theLocation and '#' not in item['word'] and item['word'] not in countryList and item['word'] not in provinces and item['score'] >=0.80:
                                theLocation = theLocation + item['word'] + ","  # append the extracted locations


            if theLocation != "":
                newsData.SetLocation(theLocation)  # add the list of locations
                newsData.SettimeStamp(
                    time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))  # give the news a time stamp
            theLocation = ""

    print("request received")
    # start of the code
    the_word = ["الأعاصير", "إطلاق نار", "زلزال", "حوادث", "زلازل", "حريق", "إرهاب", "الجرائم", "وفاتان",
                "حرب", "إصابات", "بانفجار", "حادث", "إغلاق طريق"]
    Feed = feedparser.parse('https://www.royanews.tv/rss')  # connect to royas rss

    DataList = []  # the list that will have the initial data of object news
    ImportnatnList = []

    for i in Feed.entries:
        # take every element in the list and cut the title and link
        t = str(i).split("author")[3]
        t = t.split("title")[2]
        links = t.split("base")[1]
        links = links.split("href")[1]
        links = links.split("}")[0]
        links = links.split("'")[2]
        title = t.split("value")[1]
        title = title.split("}")[0]
        title = title.split("'")[2]

        DataList.append(news(title, links))  # add the title and link to a new news object

    for data in DataList:
        for word in the_word:
            if data.GetTitle().__contains__(word):  # if the data retrived from the list of the object news titles has any word of the keywords
                tmp_data = news(data.GetTitle(), data.GetLink())
                if tmp_data not in ImportnatnList:
                    ImportnatnList.append(tmp_data)  # add the object to the filterd list

    if ImportnatnList:  # if there is a filtered list then call the extractor, and it's not empty
        extract(ImportnatnList)
    theJsonlist = []

    for newsObject in ImportnatnList:
        locations = newsObject.Getlocation()  # gets the location of the news

        newsObject.SetPoints(get_boundary_coordinates(locations))
        # if locations != "":
        #     locations = locations.split(',')  # the data is like amman,zaraqa,psut, so it splits the locations
        #     locations = list(dict.fromkeys(locations))
        #     locations.remove('')
        #     for location in locations:
        #         newsObject.SetPoints(get_boundary_coordinates(location))  # extract the coordinates of the location word
        theJsonlist.append(newsObject.getIntoList())  # turn the objects of news into a json list
        # print(theJsonlist)
    return jsonify(theJsonlist)


if __name__ == '__main__':
    app.run()
