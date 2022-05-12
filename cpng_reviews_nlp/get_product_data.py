# 크롤링 프로토타입
import concurrent.futures
import time
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import os
import json
from tqdm import tqdm

# 아래 상수들은 실제 구현에서는 변경 여지 있음!
MAX_THREADS = 30
MAX_CHAR_COUNT = 50000

# 적정 페이지 사이즈 찾기
REVIEW_PAGE_SIZE = 40

SENTENCE_DSCR = '$'
REVIEWS_PATH = '../data/sample_reviews'


def download_review_by_product(product_id):
    # Headers에 User-Agent, Cookie 중 bm_sv와 x-coupang-accept-language, 그리고 Referer 있어야 함!
    headers = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                      'Version/15.4 Safari/605.1.15',
        'Cookie': 'Cookie:bm_sv=IHATECOOKIE;x-coupang-accept-language=ko_KR;',
        'Referer': f'https://www.coupang.com/vp/products/{product_id}?isAddedCart=',
    }

    # product_name, category_id, category 가져오기
    # category_id가 내부 카테고리 id가 아니라 외부 배치(링크에 표시된 것) 기준

    # Get product_name 이름 하나 가져오려고 전체를 파싱하는 비효율적 부분
    # TODO: 상품명 가져오는 경로 개선 생각
    product_url = "https://www.coupang.com/vp/products/" + product_id
    try:
        html = requests.get(product_url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        product_name = soup.find("meta", property="og:title")["content"]
    except requests.exceptions.HTTPError as e:
        print(f"Http Error where {product_id}:", e)
        return False

    # Get product_category
    product_category_url = f"https://www.coupang.com/vp/products/{product_id}/breadcrumb-gnbmenu"

    try:
        html = requests.get(product_category_url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')

        # root category 제외
        categories = [(elem.get('href')[-6:], elem.get('title')) for elem in
                      soup.find("ul", {"id": "breadcrumb"}).find_all("a")[1:]]

    except requests.exceptions.HTTPError as e:
        print(f"Http Error where {product_id}:", e)
        return False

    # Ger reviews
    reviews = []

    # Ratings 1 to 5
    for ratings in range(1, 6):

        buffer_str = ""
        target_page = 1
        buffer_char_count = 0

        while buffer_char_count < MAX_CHAR_COUNT:
            # TODO: sortBy 선택할 수 있게 만들기
            review_page_url = f'https://www.coupang.com/vp/product/reviews?productId={product_id}&page={str(target_page)}' \
                              f'&size={REVIEW_PAGE_SIZE}&sortBy=ORDER_SCORE_ASC' \
                              f'&ratings={str(ratings)}&q=&viRoleCode=3&ratingSummary=true'
            try:
                response = requests.get(review_page_url, headers=headers)
            except requests.exceptions.HTTPError as e:
                print(f"Http Error where {product_id} page {target_page}:", e)
                return False

            html = response.text
            soup = BeautifulSoup(html, 'lxml')

            # review X
            if soup.find("div", {"class": "sdp-review__article__no-review sdp-review__article__no-review--active"}):
                break

            # 리뷰 제목과 본문
            bodies = soup.find_all("div", {"class": ["sdp-review__article__list__headline",
                                                     "sdp-review__article__list__review__content js_reviewArticleContent"]})

            buffer_str += "".join(" ".join(elem.text.split()) + SENTENCE_DSCR for elem in bodies).strip()

            target_page += 1
            buffer_char_count = len(buffer_str)

        time.sleep(0.1)

        reviews.append(buffer_str)

    # serialize_json
    json_data = OrderedDict()
    json_data["product_id"] = product_id
    json_data["product_name"] = product_name
    json_data["category"] = [{"category_id": elem[0], "category_name": elem[1]} for elem in categories]
    json_data["reviews"] = [{"rating": str(i), "data": reviews[i - 1]} for i in range(1, 6)]

    with open(os.path.join(REVIEWS_PATH, product_id + '.json'), 'w', encoding="utf-8") as make_file:
        json.dump(json_data, make_file, ensure_ascii=False, indent=4)


def download_products(product_list):
    threads = min(MAX_THREADS, len(product_list))

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(download_review_by_product, p_id) for p_id in product_list]

        # tqdm progress bar
        for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            pass


if __name__ == '__main__':
    download_products(['7958974', '130911332'])
