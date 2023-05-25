from flask import Flask, jsonify
import time
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import feedparser
from classs import news
import concurrent.futures

pd.set_option('display.max_colwidth', 500)
api_key = "AIzaSyBhW8eFNBry5bIvER254Q7pv8zdqxIJ6S4"
API_URL = "https://api-inference.huggingface.co/models/hatmimoha/arabic-ner"
headers = {"Authorization": "Bearer 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"}

app = Flask(__name__)


@app.route('/')
def index():
    def extract(news_list):
        for news_data in news_list:
            url = news_data.get_link()
            news_source = news_data.get_source()
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            if news_source == 'alghad':
                article_section = soup.find("div", id="atricle-text")
                article_section = re.sub(r'\s+', ' ', article_section.get_text())
                news_data.set_description(article_section)
            elif news_source == 'roya':
                article_section = soup.find("div", id="readMore_text")
                article_section = article_section.get_text()
                article_section = "\n".join(
                    [line.strip() for line in article_section.split("\n") if "اقرأ أيضاً" not in line.strip()])
                article_section = re.sub(r'\s+', ' ', article_section)
                news_data.set_description(article_section)

        extract_location(news_list)

    def get_boundary_coordinates(place_name):
        if place_name == "":
            return None

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
            boundary_coordinates = [(northeast["lat"], southwest["lng"]), (northeast["lat"], northeast["lng"]),
                                    (southwest["lat"], northeast["lng"]), (southwest["lat"], southwest["lng"])]
        else:
            southwest = bounds["southwest"]
            northeast = bounds["northeast"]
            boundary_coordinates = [(northeast["lat"], southwest["lng"]), (northeast["lat"], northeast["lng"]),
                                    (southwest["lat"], northeast["lng"]), (southwest["lat"], southwest["lng"])]
        return boundary_coordinates

    def get_data_and_description(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        estimated_time = 0.0
        if 'estimated_time' in response.text:
            estimated_time = response.json()['estimated_time']

        if estimated_time > 0:
            time.sleep(estimated_time)
            response = requests.post(API_URL, headers=headers, json=payload)

        return response.json()

    def extract_location(news_list):
        country_list = ["الاردن","أفغانستان","الجزائر","البحرين","بنغلاديش","بوتان","البرازيل","بروناي","بلغاريا","بوركينا فاسو","بوروندي","كمبوديا","الكاميرون","الرأس الأخضر","جمهورية أفريقيا الوسطى","تشاد","الصين","كولومبيا","جزر القمر","جمهورية الكونغو","جمهورية الكونغو الديمقراطية","كوستاريكا","كوت ديفوار","كرواتيا","كوبا","قبرص","التشيك","الدنمارك","جيبوتي","دومينيكا","جمهورية الدومينيكان","تيمور الشرقية","الإكوادور","مصر","السلفادور","غينيا الإستوائية","إريتريا","إستونيا","إثيوبيا","فيجي","فنلندا","فرنسا","الغابون","غامبيا","جورجيا","ألمانيا","غانا","اليونان","غرينادا","غواتيمالا","غينيا","غينيا-بيساو","غيانا","هايتي","هندوراس","المجر","آيسلندا","الهند","إندونيسيا","إيران","العراق","جمهورية أيرلندا","إسرائيل","إيطاليا","جامايكا","اليابان","الأردن","كازاخستان","كينيا","كيريباتي","كوريا الشمالية","كوريا الجنوبية","الكويت","قرغيزستان","لاوس","لاتفيا","لبنان","ليسوتو","ليبيريا","ليبيا", "ليختنشتاين","ليتوانيا","لوكسمبورغ","مدغشقر","مالاوي","ماليزيا","جزر المالديف","مالي","مالطا","جزر مارشال","موريتانيا","موريشيوس","المكسيك","مايكرونيزيا","مولدوفا","موناكو","منغوليا","الجبل الأسود","المغرب","موزمبيق","ميانمار","ناميبيا","ناورو","نيبال","هولندا","نيوزيلندا","نيكاراجوا","النيجر","نيجيريا","جزيرة النورفولك","مقدونيا الشمالية","النرويج","عمان","باكستان","بالاو","بنما","بابوا غينيا الجديدة","باراغواي","بيرو","الفلبين","بولندا","البرتغال","قطر","رومانيا","روسيا","رواندا","سانت كيتس ونيفيس","سانت لوسيا","سانت فينسنت والغرينادين","ساموا","سان مارينو","ساو تومي وبرينسيبي","المملكة العربية السعودية","السنغال","صربيا","سيشل","سيراليون","سنغافورة","سلوفاكيا","سلوفينيا","جزر سليمان","الصومال","جنوب إفريقيا","جنوب السودان","إسبانيا","سريلانكا","السودان","سورينام","سوازيلاند","السويد","سويسرا","سوريا","تايوان","طاجيكستان","تنزانيا","تايلاند","توغو","تونجا","ترينداد وتوباغو", "تركيا","تركمانستان","توفالو","أوغندا","أوكرانيا","الإمارات العربية المتحدة","المملكة المتحدة","الولايات المتحدة الأمريكية","أوروغواي","أوزبكستان","فانواتو","فنزويلا","فيتنام","اليمن","زامبيا","زيمبابوي","أمريكا"]
        provinces = ["عجلون", "العقبة", "الزرقاء", "السلط", "جرش", "الكرك", "معان", "المفرق", "مادبا", "عمان",
                     "الطفيلة", "إربد"]
        for news_data in news_list:
            if news_data.get_description() != '':
                response = get_data_and_description(news_data.get_description())
                for item in response:
                    if isinstance(item, dict) and 'entity_group' in item:
                        if item['entity_group'] == 'LOCATION' and \
                                item['word'] not in news_data.get_location() and \
                                '#' not in item['word'] and \
                                item['word'] not in country_list and\
                                item['word'] not in provinces and item['score'] >= 0.80:
                            news_data.add_location(item['word'])

    print("Request received")
    the_word = ["الأعاصير", "إطلاق نار", "زلزال", "حوادث", "زلازل", "حريق", "إرهاب", "الجرائم", "التطورات", "حرب",
                "إصابات", "بانفجار", "حادث", "إغلاق طريق", "فاجعة", "إصابة"]
    news_websites = [['https://www.royanews.tv/rss', 'roya'], ['https://www.alghad.com/rss', 'alghad']]
    data_list = []
    important_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:

        for website in news_websites:
            feed = feedparser.parse(website[0])
            for entry in feed.entries:
                data_list.append(news(entry['title'], entry['id'], website[1], entry['updated']))

        for data in data_list:
            for word in the_word:
                if data.get_title().__contains__(word):

                    if data not in important_list:
                        important_list.append(data)

        executor.map(extract, [important_list])  # Concurrently extract data for each news object

    the_json_list = []
    with concurrent.futures.ThreadPoolExecutor() as _:
        for news_object in important_list:
            locations = news_object.get_location()
            boundary = get_boundary_coordinates(locations)

            if boundary is not None:
                news_object.set_points(boundary)
                the_json_list.append(news_object.to_dict())

    return jsonify(the_json_list)


if __name__ == '__main__':
    app.run()
