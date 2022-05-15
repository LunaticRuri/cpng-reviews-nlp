import os.path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import math


class CoupangCategoryFetcher:
    # TODO: tree는 그래도 놔두고 product_list만 update하는 부분 추가

    headers = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                      'Version/15.4 Safari/605.1.15',
        'Cookie': 'bm_sv=IHATECOOKIE;x-coupang-accept-language=ko_KR;',
        'Referer': 'https://www.coupang.com/',
    }

    category_url = "https://www.coupang.com/np/categories/"

    ALL = 0

    def __init__(
            self,
            root_category_id,
            max_product_count,
            file_path,
            update,
            max_thread,
    ):
        """CoupangCategoryFetcher 생성자

        :param root_category_id: 최상위 카테고리, 만약 self.ALL(=0)이면 전체 카테고리
        :type root_category_id:str
        :param max_product_count: 카테고리별 최대 상품 수
        :type max_product_count: int
        :param file_path: 카테고리 구조를 저장할 경로(파일 이름까지 포함), 파일 형식은 json
        :type file_path: str
        :param update: 업데이트 여부 - 참이면 경로에 파일이 있어도 새로 받아옴, 기본 값이 참
        :type update: bool
        :param max_thread: 최대 스레드 개수 기본 값은 40으로 설정되어 있음
        :type max_thread: int
        """

        self.root_category_id = root_category_id
        self.max_product_count = max_product_count
        self.max_thread = max_thread
        self.file_path = file_path
        self.update = update

        self.soup_count = 0

        if self.root_category_id == "all":
            self.start_depth = self.ALL
        else:
            url = self.category_url + self.root_category_id
            target_soup = self.get_soup(url).find("div", {"class": "search-result"})

            # 존재하지 않는 category_id
            if not target_soup:
                raise SystemExit(f"Category: {self.root_category_id} doesn't exist")
            # second와 sub에서 사용되는 depth 기준과 맞춰주기 위해 -1
            self.start_depth = len(target_soup.find_all("li")) - 1

        self.category_tree = {}

    def __repr__(self):
        repr_dict = {
            "root_category_id": self.root_category_id,
            "max_product_count": self.max_product_count,
            "max_thread": self.max_thread,
            "file_path": self.file_path,
            "update": self.update,
        }
        return str(repr_dict)

    def get_soup(self, url):
        """ url로 가져온 웹사이트를 파싱해 BeautifulSoup 객체로 만든다.
        :param url: 웹사이트 주소
        :type url: str
        :return: 사이트 html 전체의 BeautifulSoup 객체
        :rtype: BeautifulSoup
        """
        try:
            response = requests.get(url, headers=CoupangCategoryFetcher.headers)
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        time.sleep(0.1)

        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        self.soup_count += 1

        return soup

    @staticmethod
    def get_internal_id(category_id):
        """category_id를 internal_category_id로 바꾼다.
        :param category_id: 카테고리 id = ~/np/categories/ 뒤에 붙는 6자리 코드
        :type category_id: str
        :return: internal_category_id
        :rtype: str
        """
        return str(int(category_id) - 100)

    # for test
    @staticmethod
    def get_all_category_iter(dictionary):
        for key, value in dictionary.items():
            if type(value) is dict:
                yield key, value
                yield from CoupangCategoryFetcher.get_all_category_iter(value)
            else:
                yield key, value

    def read_json_category_tree(self):
        """전달받은 file_path에서 json file을 읽어서 category_tree로 내보낸다.
        :return: 파일이 정상이면 category structure를 나타낼 수 있는 nested dict,
         아니면 empty dict.
        :rtype: dict
        """
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path) as jf:
                    category_tree = json.load(jf)
            except json.JSONDecodeError:
                print(f"Unexpected format:{self.file_path}")
                return {}
        else:
            print(f"Can't find '{self.file_path}'")
            return {}

        return category_tree

    def write_json_category_tree(self):
        """
        category_tree 받아와 json file로 file_path에 저장하는 함수
        """
        with open(self.file_path, "w+") as jf:
            json.dump(self.category_tree, jf, indent=4, ensure_ascii=False)

    # dirty code(dependency between methods and duplication) -> but refactoring is time-consuming job (

    def get_category_tree(self):
        """ 카테고리 구조 반환 함수(외부 접근용)

        :return: category structure를 나타낼 수 있는 nested dictionary
        :rtype: dict
        """

        print("Fetching category data...")


        #  TODO: 불러온 파일이 원하는 데이터 아닐 경우 예외 처리 구현
        if not self.update:
            self.category_tree = self.read_json_category_tree()
            if self.category_tree:
                print(f"Reading {self.file_path}...")
                return self.category_tree

        # Multithreading
        if self.start_depth == self.ALL:
            print("This will take a long time. (")
            print("Fetching first level categories...")
            self.category_tree = self._first_category_parser()

            print("Fetching second level categories...")
            for key in tqdm(self.category_tree.keys(), total=len(self.category_tree)):
                self.category_tree[key]["children"] = self._second_category_parser(key)

            print("Fetching subcategories...")
            for key in tqdm(self.category_tree.keys(), total=len(self.category_tree)):
                with ThreadPoolExecutor(max_workers=self.max_thread) as executor:
                    futures = []
                    for c_id in self.category_tree[key]["children"].keys():
                        futures.append(executor.submit(self._sub_category_parser, c_id))

                    for f in as_completed(futures):
                        c_id, c_children = f.result()

                        category_name = self.category_tree[key]["children"].get(c_id)["category_name"]
                        internal_id = self.get_internal_id(c_id)
                        _, product_list = self._get_product_list_by_category(c_id)

                        self.category_tree[key]["children"][c_id] = {
                            "category_name": category_name,
                            "internal_category_id": internal_id,
                            "product_list": product_list,
                            "children": c_children,
                        }

        elif self.start_depth == 1:
            print("Fetching second level categories...")

            top_categories = self._second_category_parser(self.root_category_id)

            print("Fetching subcategories...")
            threads = min(self.max_thread, len(top_categories))

            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for c_id in top_categories.keys():
                    futures.append(executor.submit(self._sub_category_parser, c_id))

                # tqdm progress bar
                for f in tqdm(as_completed(futures), total=len(futures)):
                    c_id, c_children = f.result()

                    category_name = top_categories.get(c_id)["category_name"]
                    internal_id = self.get_internal_id(c_id)
                    _, product_list = self._get_product_list_by_category(c_id)

                    self.category_tree[c_id] = {
                        "category_name": category_name,
                        "internal_category_id": internal_id,
                        "product_list": product_list,
                        "children": c_children,
                    }

        else:
            print("Fetching subcategories...")
            _, self.category_tree = self._sub_category_parser(self.root_category_id, self.start_depth)

        self.write_json_category_tree()

        print("get_soup: ", self.soup_count)

        return self.category_tree

    PAGE_LIST_SIZE = 120

    def _get_product_list_by_category(self, category_id):

        # sorter 설정할 수 있게 하기
        # 정렬 기준이 판매량임
        category_first_page_url = f"https://www.coupang.com/np/categories/194627?" \
                                  f"listSize={self.PAGE_LIST_SIZE}&page=1&sorter=saleCountDesc"

        soup = self.get_soup(category_first_page_url).find("ul", {"class": "baby-product-list"})["data-products"]

        # 비어 있을 때
        if not soup:
            print(category_id, '@@@@@@@@@@@@@@@@@@@@@@')
            return category_id, []
        # TODO: 에러 못잡으면 try로 soup 출력
        try:
            target_dict = eval(soup)
        except:
            print(category_id)
            print(soup)

        max_page = int(target_dict['productTotalPage'])

        # 불러올 페이지 수 계산
        end_page = math.ceil(self.max_product_count / CoupangCategoryFetcher.PAGE_LIST_SIZE) \
            if self.max_product_count / CoupangCategoryFetcher.PAGE_LIST_SIZE < max_page else max_page
        product_list = []

        for page in range(1, end_page + 1):
            category_page_url = f"https://www.coupang.com/np/categories/194627?" \
                  f"listSize={CoupangCategoryFetcher.PAGE_LIST_SIZE}&page={page}&sorter=saleCountDesc"

            soup = self.get_soup(category_page_url)

            target_dict = eval(soup.find("ul", {"class": "baby-product-list"})["data-products"])
            target_list = target_dict['indexes']

            product_list.extend(target_list)

        # list 길이 최대 상품 수에 맞추어 잘라내기
        if len(product_list) > self.max_product_count:
            product_list = product_list[:self.max_product_count]

        return category_id, product_list

    def _sub_category_parser(self, p_category_id, depth=2):
        """ 쿠팡 카테고리 3단계 이하 크롤링 메소드(내부용)
        예시) 식품 -> 면/통조림/가공식품 -> 라면/컵라면 -> ... 라면/컵라면 이하 카테고리 해당
        2단계 카테고리 이후로는 같은 방법으로 정보를 가져올 수 있기에 재귀 사용됨

        :param str p_category_id: 직전 상위 카테고리의 id, 링크 접근에 필요함.
        :param int depth: 같은 층위를 구분하여 가져옴.
        :returns: (p_category_id, subclasses)
        """
        # 접근 시 페이지 category_id("data-linkcode")랑 다른 category_internal_id("data-component-id")써야 함!
        p_internal_id = self.get_internal_id(p_category_id)
        url = f'https://www.coupang.com/np/search/getFirstSubCategory?channel=&component={p_internal_id}'

        soup = self.get_soup(url)

        subclasses = {}

        # 같은 깊이만 탐색
        sub_li_list = []
        is_end_of_category = True
        for elem in soup.find_all("li"):
            if eval(elem.label["data-coulog"])["depth"] == str(depth):
                sub_li_list.append(elem)
                is_end_of_category = False

        # 카테고리 상위 부분 말단
        if is_end_of_category:
            return p_category_id, {}

        for elem in sub_li_list:
            children = {}

            if elem["data-campaign-id"] != "":
                continue

            category_name = elem.label.text
            print(depth, category_name)
            # elem["data-linkcode"]는 웹페이지 링크에서 보임
            category_id = elem["data-linkcode"]
            # subcategory 접근할 때 필요한 내부 id -> elem["data-component-id"] 로도 접근 가능
            internal_category_id = self.get_internal_id(category_id)

            _, product_list = self._get_product_list_by_category(category_id)

            if elem.find("ul", {"class": "search-option-items-child"}):
                _, children = self._sub_category_parser(category_id, depth + 1)

            subclasses[category_id] = {
                "category_name": category_name,
                "internal_category_id": internal_category_id,
                "product_list": product_list,
                "children": children,
            }

        return p_category_id, subclasses

    def _second_category_parser(self, p_category_id):
        """쿠팡 카테고리 2단계 크롤링 메소드(내부용)
        예시) 식품 -> 면/통조림/가공식품 에서 '면/통조림/가공식품'
        :param p_category_id: 직전 상위 카테고리 id, 링크 접근에 필요함.
        :returns: second_classes
        """
        # category page link
        url = self.category_url + p_category_id

        target_soup = self.get_soup(url).find("div", {"class": "search-filter-options search-category-component"})
        second_li_list = target_soup.find_all("li")

        second_classes = {}

        for elem in second_li_list:

            # campaign page는 실제 카테고리 분류가 아니기 떄문에 제외함
            if elem["data-campaign-id"] != "":
                continue

            category_name = elem.label.text
            # elem["data-linkcode"]는 웹페이지 링크에서 보임
            category_id = elem["data-linkcode"]
            # subcategory 접근할 때 필요한 내부 id -> elem["data-component-id"] 로도 접근 가능
            internal_category_id = self.get_internal_id(category_id)

            _, product_list = self._get_product_list_by_category(category_id)

            second_classes[category_id] = {
                "category_name": category_name,
                "internal_category_id": internal_category_id,
                "product_list": product_list,
                "children": {},
            }

        threads = min(self.max_thread, len(second_li_list))

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for c_id in second_classes.keys():
                futures.append(executor.submit(self._get_product_list_by_category, c_id))

            for f in as_completed(futures):
                c_id, product_list = f.result()
                second_classes[c_id]["product_list"] = product_list

        return second_classes

    def _first_category_parser(self):
        """ 쿠팡 카테고리 1단계 크롤링 메소드(내부용)
        쿠팡 메인화면에서 1단계 최상위 분류 가져옴.
        예시) 식품
        :return: 쿠팡 전체의 category structure를 나타낼 수 있는 nested dictionary
        :rtype: dict
        """
        # 메인화면에서 긁어올 수 있는 분류는 더보기 때문에 한정되어 있음.
        # 그래서 대분류 별로 페이지에 직접 들어가서 처리해주어야 함.

        # Main page
        url = 'https://www.coupang.com/'

        soup = self.get_soup(url)

        # 최상위 분류
        first_classes = {}

        first_iter = soup.find("ul", {"class": "menu shopping-menu-list"}).find_all('li', recursive=False)

        for first_sub in first_iter:

            # 빈칸일 경우
            if first_sub.a is None:
                continue

            # '패션의류/잡화'는 실제 분류가 아님. 그 밑의 분류를 최상위로 해야 함
            if first_sub.a['href'] == 'javascript:;':
                for first_sub2 in first_sub.find_all('li', {"class": "second-depth-list"}):
                    category_id = first_sub2.a['href'][-6:]
                    category_name = first_sub2.a.get_text(strip=True)
                    _, product_list = self._get_product_list_by_category(category_id)

                    first_classes[category_id] = {
                        "category_name": category_name,
                        "internal_category_id": "",
                        "product_list": product_list,
                        "children": {},
                    }
            # 나머지 대분류
            else:
                category_id = first_sub.a['href'][-6:]
                category_name = first_sub.a.get_text(strip=True)
                _, product_list = self._get_product_list_by_category(category_id)
                first_classes[category_id] = {
                    "category_name": category_name,
                    "internal_category_id": "",
                    "product_list": product_list,
                    "children": {},
                }

        # Multithreading
        threads = min(self.max_thread, len(first_classes))

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for c_id in first_classes.keys():
                futures.append(executor.submit(self._get_product_list_by_category, c_id))

            # tqdm progress bar
            for f in tqdm(as_completed(futures), total=len(futures)):
                c_id, product_list = f.result()
                first_classes[c_id]["product_list"] = product_list

        return first_classes
