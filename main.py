from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account.
cred = credentials.Certificate("shirobara-blog-firebase-adminsdk-t17cn-bace8d0cf6.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()
driver = webdriver.Chrome(
    executable_path="/Users/kataokayuuki/Desktop/ばら日誌スクレイピング/chromedriver_113"
)


def setDoc(dic):
    db.collection("articles").document(str(dic["postAt"])).set(dic)


driver.get("http://shirobarakai.blog44.fc2.com/")
time.sleep(2)

while True:
    print("-------------new page---------------")
    for i in range(50):
        try:
            date_text = driver.find_element(
                By.XPATH, f'//*[@id="content"]/div[{i + 1}]/h3'
            ).text
            title_text = driver.find_element(
                By.XPATH, f"/html/body/div[2]/div[1]/div[{i + 1}]/h4"
            ).text
            article_text = driver.find_element(
                By.XPATH, f'//*[@id="content"]/div[{i + 1}]/div'
            ).text
            time_text = driver.find_element(
                By.XPATH, f'//*[@id="content"]/div[{i + 1}]/ul/li[1]/a'
            ).text

            images = []

            try:
                single_image_element = driver.find_element(
                    By.XPATH, f'//*[@id="content"]/div[{i + 1}]/div/a/img'
                )
                single_img_url = single_image_element.get_attribute("src")
                images.append(single_img_url)
            except Exception as e:
                print("ERROR")
                images = []
                for j in range(5):
                    try:
                        image_element = driver.find_element(
                            By.XPATH,
                            f'//*[@id="content"]/div[{i + 1}]/div/div[{j+1}]/a/img',
                        )
                        print("found")
                        img_url = image_element.get_attribute("src")
                        images.append(img_url)
                    except Exception as e:
                        print("error")
                        break

            # firestoreに追加されるときに改行コードが反映されないから別の文字列に置換しておく
            # print(date_text, title_text, article_text.replace("\n", "%n"), time_text)

            dt = datetime.datetime.strptime(
                f"{date_text[:10]} {time_text}", "%Y-%m-%d %H:%M:%S"
            )
            # datetime  → タイムスタンプ
            ts = int(datetime.datetime.timestamp(dt))

            article = {
                "title": title_text,
                "text": article_text.replace("\n", "%n"),
                "postAt": ts,
                "images": images if len(images) > 0 else None,
            }
            # print(article)
            setDoc(article)
            print(article)
            images = []
            time.sleep(0.5)

            # ここにfirestoreに追加してsleepする処理を追加(非同期処理のほうがいいかも)
            # date_textとtime_textから投稿日時のタイムスタンプを作成する
            # タイトル, 記事本文, 投稿日時
        except:
            time.sleep(0.2)
            images = []
            break

    prev_btn = driver.find_element(By.XPATH, f'//*[@id="pagenavi"]/tbody/tr/td[3]/a')
    prev_btn.click()
