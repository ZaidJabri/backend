from flask import Flask, jsonify
import time
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import feedparser
from News import News
import concurrent.futures

pd.set_option('display.max_colwidth', 500)
api_key = "AIzaSyBhW8eFNBry5bIvER254Q7pv8zdqxIJ6S4"
API_URL = "https://api-inference.huggingface.co/models/hatmimoha/arabic-ner"
headers = {"Authorization": "Bearer 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"}

app = Flask(__name__)


@app.route('/')
def index():
    def get_boundary_coordinates(place_name):
        """
        Retrieves the boundary coordinates for a given place name using the Google Geocoding API.
        """

        if place_name == "":
            return None

        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place_name}&key={api_key}"
        response = requests.get(geocode_url, timeout=3000)
        response_json = response.json()
        results = response_json["results"]

        if len(results) == 0:
            return None

        result = results[0]
        geometry = result["geometry"]
        location = geometry["location"]
        bounds = geometry.get("bounds")

        if bounds is None:
            # Return the single coordinate point
            print(location)
            return [(location["lat"], location["lng"])]
        else:
            viewport = geometry["viewport"]
            southwest = viewport["southwest"]
            northeast = viewport["northeast"]
            boundary_coordinates = [(northeast["lat"], southwest["lng"]), (northeast["lat"], northeast["lng"]),
                                    (southwest["lat"], northeast["lng"]), (southwest["lat"], southwest["lng"])]
            print(boundary_coordinates)
            return boundary_coordinates

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
        country_list = ["الاردن", "أفغانستان", "الجزائر", "البحرين", "بنغلاديش", "بوتان", "البرازيل", "بروناي",
                        "بلغاريا", "بوركينا فاسو", "بوروندي", "كمبوديا", "الكاميرون", "الرأس الأخضر",
                        "جمهورية أفريقيا الوسطى", "تشاد", "الصين", "كولومبيا", "جزر القمر", "جمهورية الكونغو",
                        "جمهورية الكونغو الديمقراطية", "كوستاريكا", "كوت ديفوار", "كرواتيا", "كوبا", "قبرص", "التشيك",
                        "الدنمارك", "جيبوتي", "دومينيكا", "جمهورية الدومينيكان", "تيمور الشرقية", "الإكوادور", "مصر",
                        "السلفادور", "غينيا الإستوائية", "إريتريا", "إستونيا", "إثيوبيا", "فيجي", "فنلندا", "فرنسا",
                        "الغابون", "غامبيا", "جورجيا", "ألمانيا", "غانا", "اليونان", "غرينادا", "غواتيمالا", "غينيا",
                        "غينيا-بيساو", "غيانا", "هايتي", "هندوراس", "المجر", "آيسلندا", "الهند", "إندونيسيا", "إيران",
                        "العراق", "جمهورية أيرلندا", "إسرائيل", "إيطاليا", "جامايكا", "اليابان", "الأردن", "كازاخستان",
                        "كينيا", "كيريباتي", "كوريا الشمالية", "كوريا الجنوبية", "الكويت", "قرغيزستان", "لاوس",
                        "لاتفيا", "لبنان", "ليسوتو", "ليبيريا", "ليبيا", "ليختنشتاين", "ليتوانيا", "لوكسمبورغ",
                        "مدغشقر", "مالاوي", "ماليزيا", "جزر المالديف", "مالي", "مالطا", "جزر مارشال", "موريتانيا",
                        "موريشيوس", "المكسيك", "مايكرونيزيا", "مولدوفا", "موناكو", "منغوليا", "الجبل الأسود", "المغرب",
                        "موزمبيق", "ميانمار", "ناميبيا", "ناورو", "نيبال", "هولندا", "نيوزيلندا", "نيكاراجوا", "النيجر",
                        "نيجيريا", "جزيرة النورفولك", "مقدونيا الشمالية", "النرويج", "عمان", "باكستان", "بالاو", "بنما",
                        "بابوا غينيا الجديدة", "باراغواي", "بيرو", "الفلبين", "بولندا", "البرتغال", "قطر", "رومانيا",
                        "روسيا", "رواندا", "سانت كيتس ونيفيس", "سانت لوسيا", "سانت فينسنت والغرينادين", "ساموا",
                        "سان مارينو", "ساو تومي وبرينسيبي", "المملكة العربية السعودية", "السنغال", "صربيا", "سيشل",
                        "سيراليون", "سنغافورة", "سلوفاكيا", "سلوفينيا", "جزر سليمان", "الصومال", "جنوب إفريقيا",
                        "جنوب السودان", "إسبانيا", "سريلانكا", "السودان", "سورينام", "سوازيلاند", "السويد", "سويسرا",
                        "سوريا", "تايوان", "طاجيكستان", "تنزانيا", "تايلاند", "توغو", "تونجا", "ترينداد وتوباغو",
                        "تركيا", "تركمانستان", "توفالو", "أوغندا", "أوكرانيا", "الإمارات العربية المتحدة",
                        "المملكة المتحدة", "الولايات المتحدة الأمريكية", "أوروغواي", "أوزبكستان", "فانواتو", "فنزويلا",
                        "فيتنام", "اليمن", "زامبيا", "زيمبابوي", "أمريكا"]
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
                                item['word'] not in country_list and \
                                item['word'] not in provinces and item['score'] >= 0.90:
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
                data_list.append(News(entry['title'], entry['id'], website[1], entry['updated']))

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
                the_json_list.append(news_object.to_dictionary())
    n = News("test", "ttt", 'roya', '2020-06-20T12:00:00+00:00')
    n.id = 1
    n.set_points([(31.80420856281328, 35.93924239243781), (31.79873072569502, 35.928608576755565),
                  (31.793685584020597, 35.93283729637047), (31.798168869130702, 35.94312281493864)])
    n.set_description("testing news for zaid ")
    n.set_location("ghazi")
    n.set_timestamp(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
    the_json_list.append(n.to_dictionary())
    n = News("t1", "ttt", 'roya', '2020-06-20T12:00:00+00:00')
    n.id = 12
    n.set_points([(31.908709199196878, 35.86460066505852), (31.905926340099864, 35.86996509881537),
                  (31.90318375673667, 35.86649807419722), (31.906260795887317, 35.86154705793928)])
    n.set_description("testing news for issa ")
    n.set_location("ghazi")
    n.set_timestamp(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
    the_json_list.append(n.to_dictionary())
    n = News("t2", "ttt", 'roya', '2020-06-20T12:00:00+00:00')
    n.id = 19
    n.set_points([(31.906181429198234, 35.866832293687814)])
    n.set_description("testing news for issa ")
    n.set_location("ghazi")
    n.set_timestamp(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
    the_json_list.append(n.to_dictionary())
    n = News("t3", "ttt", 'roya', '2020-06-20T12:00:00+00:00')
    n.id = 88
    n.set_points([(31.9071986213631, 35.86566611909778)])
    n.set_description("testing news for issa ")
    n.set_location("ghazi")
    n.set_timestamp(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
    the_json_list.append(n.to_dictionary())
    n = News("t4", "ttt", 'roya', '2020-06-20T12:00:00+00:00')
    n.id = 83
    n.set_points([(31.911177484211002, 35.86129809534054), (31.90841876917848, 35.86751099463854),
                  (31.905751011534086, 35.86335920024101), (31.908631317563408, 35.858702648400275)])
    n.set_description("testing news for issa ")
    n.set_location("ghazi")
    n.set_timestamp(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
    the_json_list.append(n.to_dictionary())
    n = News("جامعة الأميرة سمية للتكنولوجيا", "ttt", 'roya', '2020-06-20T12:00:00+00:00')
    n.id = 3
    n.set_points([(32.02360409210125, 35.87623861433755)])
    n.set_description(
        "تأسست الجامعة عام 1991 باسم كلية الأميرة سمية الجامعية للتكنولوجيا، وكانت تمنح درجة البكالوريوس في علم الحاسبات الإلكترونية. وهي الذراع الأكاديمي للجمعية العلمية الملكية التي أسست الجامعة. وفي عام 1992، قام جلالة المغفور له الملك الحسين بن طلال بافتتاح الجامعة رسميّاً. وفي عام 1995، تم تخريج الفوج الأول من طلبة الجامعة وعددهم 72 طالباً وطالبة. وفي عام 1994، وضع حجر الأساس لكلية الملك عبد الله الثاني للهندسة الكهربائية، التي كانت تمنح آنذاك درجة البكالوريوس في الهندسة الإلكترونية. وفي عام 2002، تم اعتماد المسمى الجديد للجامعة وهو جامعة الأميرة سمية للتكنولوجيا، بالإضافة إلى استحداث تخصص جديد هو هندسة الحاسوب. توسعت الجامعة عام 2005، باستحداث تخصصات جديدة هي: هندسة الاتصالات، ونظم المعلومات الإدارية، وعلم الرسم الحاسوبي وهو الأول من نوعه في الأردن. أقرت وزارة التعليم العالي والبحث العلمي عام 2007 أنظمة الجامعة وتعليماتها، وأصبحت نموذجاً للجامعات الخاصة في الأردن. تم في عام 2007، طرح برنامج ماجستير علم الحاسوب، تلاه برنامج ماجستير تكنولوجيا البيئة وإدارتها عام 2008، ثم برنامج ماجستير إدارة الأعمال الدولية عام 2008، بالتعاون مع جامعة لانكستر/ بريطانيا.")
    n.set_location("جامعة الأميرة سمية")
    n.set_timestamp(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
    the_json_list.append(n.to_dictionary())

    return jsonify(the_json_list)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
