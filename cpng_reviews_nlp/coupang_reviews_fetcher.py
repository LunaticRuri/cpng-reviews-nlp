from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import json
import copy
import urllib3
import pickle


class CoupangReviewsFetcher:
    HEADERS = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                      'Version/15.4 Safari/605.1.15',
        'Cookie': 'Cookie:bm_sv=IHATECOOKIE;x-coupang-accept-language=ko_KR;',
        'Referer': f'https://www.coupang.com/',
    }

    def __init__(
            self,
            product_set,
            reviews_path,
            reviews_update,
            max_thread,
            max_char_count,
            work_ch = '0',  # tmp
    ):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.product_set = product_set
        self.max_thread = max_thread
        self.reviews_update = reviews_update
        self.max_char_count = max_char_count
        self.reviews_path = reviews_path
        self.soup_count = 0

        self.work_ch = work_ch  #tmp

    def __repr__(self):
        pass

    def get_soup(self, url):
        """ url로 가져온 웹사이트를 파싱해 BeautifulSoup 객체로 만든다.
        :param url: 웹사이트 주소
        :type url: str
        :return: 사이트 html 전체의 BeautifulSoup 객체
        :rtype: BeautifulSoup
        """
        try:
            response = requests.get(url, headers=self.HEADERS, verify=False)
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        except requests.exceptions.ConnectionError:
            return False

        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        self.soup_count += 1

        time.sleep(0.5)

        return soup

    def get_soup_count(self):
        return self.soup_count

    def get_reviews(self):

        get_count = 0

        product_work_set = copy.deepcopy(self.product_set)

        if not self.reviews_update:
            for elem in self.product_set:
                if self.is_review_exists(elem):
                    product_work_set.discard(elem)

        if not product_work_set:
            return True

        threads = min(self.max_thread, len(product_work_set))

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for p_id in product_work_set:
                futures.append(executor.submit(self.fetch_review_by_product, p_id))

            # tqdm progress bar
            for f in tqdm(as_completed(futures), total=len(product_work_set)):
                is_success = f.result()
                if type(is_success) is str:
                    if not self.work_ch == '0':
                        try:
                            with open('../data/dividing/err_' + self.work_ch + '.pickle', 'rb') as fp:
                                err_set = pickle.load(fp)
                        except EOFError:
                            err_set = set()
                        with open('../data/dividing/err_' + self.work_ch + '.pickle', 'wb') as fp:
                            err_set.add(is_success)
                            pickle.dump(err_set,fp)

                else:
                    get_count += 1

        print(get_count, len(product_work_set), get_count / len(product_work_set))

    def is_review_exists(self, product_id):
        if os.path.isfile(os.path.join(self.reviews_path, str(product_id) + '.json')):
            return True
        else:
            return False

    # listSize는 60 아니면 120 밖에 안됨 -> 60으로 하면 오버헤드
    PAGE_LIST_SIZE = 120
    REVIEW_PAGE_SIZE = 40
    SENTENCE_DSCR = '\n'

    def fetch_review_by_product(self, product_id):

        # product_name, category_id, category 가져오기
        # category_id가 내부 카테고리 id가 아니라 외부 배치(링크에 표시된 것) 기준

        product_url = f"https://www.coupang.com/vp/products/{product_id}"
        soup = self.get_soup(product_url)

        if not soup:
            print(product_id, ": can't find the page")
            return str(product_id)

        try:
            product_name = soup.find("meta", property="og:title")["content"]
        except TypeError:
            print(product_id, "Access denied or 19")
            return str(product_id)

        # Get product_category
        # 쿠팡 카테고리 구조가 내부와 외부 카테고리 구조가 달라서, CategoryFetcher에서 받아온 것과 다를 수 있음
        # 뭘 기준으로 해야 할 지는 아직 정하지는 않았음
        # 외부 기준으로 하면 중복 문제가 발생하지만, 수가 구형 이슈 발생 x
        # 내부 기준으로 하면 파일 받아오고 그 파일을 바탕으로 다시 구조를 만들어야 함

        product_category_url = f"https://www.coupang.com/vp/products/{product_id}/breadcrumb-gnbmenu"
        soup = self.get_soup(product_category_url)

        if not soup:
            print(product_id, ": can't find the category bar 1")
            return str(product_id)

        categories = []
        try:
            for elem in soup.find("ul", {"id": "breadcrumb"}).find_all("a")[1:]:
                categories.append((elem.get('href')[-6:], elem.get('title')))
        except:  # TypeError, Attribute Error
            print(product_id, ": can't find the category bar 2")
            return str(product_id)

        # Ger reviews
        reviews = []
        # Ratings 1 to 5
        for ratings in range(1, 6):

            buffer_str = ""
            target_page = 1
            buffer_char_count = 0

            while buffer_char_count < self.max_char_count:

                if target_page > 20:
                    break

                review_page_url = f'https://www.coupang.com/vp/product/reviews?' \
                                  f'productId={product_id}&page={str(target_page)}' \
                                  f'&size={self.REVIEW_PAGE_SIZE}&sortBy=ORDER_SCORE_ASC' \
                                  f'&ratings={str(ratings)}&q=&viRoleCode=3&ratingSummary=true'

                soup = self.get_soup(review_page_url)

                if not soup:
                    print(product_id, ": can't find the reviews")
                    return str(product_id)

                # review X
                if soup.find("div", {"class": "sdp-review__article__no-review sdp-review__article__no-review--active"}):
                    break

                # 리뷰 제목과 본문
                bodies = soup.find_all(
                    "div",
                    {"class":
                         ["sdp-review__article__list__headline",
                          "sdp-review__article__list__review__content js_reviewArticleContent"]})

                buffer_str += "".join(" ".join(elem.text.split()) + self.SENTENCE_DSCR for elem in bodies).strip()

                target_page += 1
                buffer_char_count = len(buffer_str)

            reviews.append(buffer_str)

        # serialize_json
        json_data = {
            "product_id": product_id,
            "product_name": product_name,
            "category": [{"category_id": elem[0], "category_name": elem[1]} for elem in categories],
            "reviews": [{"rating": str(i), "data": reviews[i - 1]} for i in range(1, 6)],
        }

        with open(os.path.join(self.reviews_path, str(product_id) + '.json'), 'w+', encoding="utf-8") as make_file:
            json.dump(json_data, make_file, ensure_ascii=False, indent=4)

        return True
