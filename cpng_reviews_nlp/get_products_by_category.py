# 상품 목록 크롤링 프로토타입
import math
import requests
from bs4 import BeautifulSoup

# 아래 상수들은 실제 구현에서는 변경 여지 있음!

MAX_PRODUCTS_COUNT = 200

# listSize는 60 아니면 120 밖에 안됨
PAGE_LIST_SIZE = 120


def get_product_list(category_id):
    # Headers에 User-Agent, Cookie 중 bm_sv와 x-coupang-accept-language, 그리고 Referer 있어야 함!
    headers = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                      'Version/15.4 Safari/605.1.15',
        'Cookie': 'Cookie:bm_sv=IHATECOOKIE;x-coupang-accept-language=ko_KR;',
        'Referer': 'https://www.coupang.com/',
    }

    # sorter 설정할 수 있게 하기
    # 정렬 기준이 판매량임
    category_first_page_url = f"https://www.coupang.com/np/categories/194627?listSize={PAGE_LIST_SIZE}&page=1&sorter=saleCountDesc"

    try:
        html = requests.get(category_first_page_url, headers=headers).text
    except requests.exceptions.HTTPError as e:
        print(f"Http Error where category: {category_id}", e)
        return False

    target_dict = eval(BeautifulSoup(html, 'lxml').find("ul", {"class": "baby-product-list"})["data-products"])
    max_page = int(target_dict['productTotalPage'])

    # 불러올 페이지 수 계산
    end_page = math.ceil(MAX_PRODUCTS_COUNT / PAGE_LIST_SIZE) if MAX_PRODUCTS_COUNT / PAGE_LIST_SIZE < max_page else max_page

    product_list = []

    for page in range(1, end_page+1):
        url = f"https://www.coupang.com/np/categories/194627?listSize={PAGE_LIST_SIZE}&page={page}&sorter=saleCountDesc"

        try:
            html = requests.get(url, headers=headers).text
        except requests.exceptions.HTTPError as e:
            print(f"Http Error where category: {category_id}", e)
            return False

        target_dict = eval(BeautifulSoup(html, 'lxml').find("ul", {"class": "baby-product-list"})["data-products"])
        target_list = target_dict['indexes']

        product_list.extend(target_list)

    # list 길이 최대 상품 수에 맞추어 잘라내기
    if len(product_list) > MAX_PRODUCTS_COUNT:
        product_list = product_list[:MAX_PRODUCTS_COUNT]

    return product_list


if __name__ == '__main__':
    print(get_product_list("194686"))
