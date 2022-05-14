import json
import concurrent.futures
import time
import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm


class CoupangCategoryWriter:

    headers = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                      'Version/15.4 Safari/605.1.15',
        'Cookie': 'bm_sv=IHATECOOKIE;x-coupang-accept-language=ko_KR;',
        'Referer': 'https://www.coupang.com/',
    }

    category_url = "https://www.coupang.com/np/categories/"

    ALL = -1

    def __init__(
            self,
            root_category_id,
            file_path,
            update,
    ):
        if root_category_id == "all":
            self.depth = self.ALL
            self.start_point = self.first_category_parser
        else:
            url = self.category_url.join(root_category_id)

            target_soup = self.get_soup(url).find("div",{"class":"search-result"})

            # 존재하지 않는 category_id
            if not target_soup:
                raise SystemExit(f"Category: {root_category_id} doesn't exist")

            # second와 sub에서 사용되는 depth 기준과 맞춰주기 위해 -2
            self.depth = len(target_soup.find_all("li")) - 2

            if self.depth == 1:
                self.start_point = self.second_category_parser()
            else:
                pass

    def __repr__(self):
        pass

    @staticmethod
    def get_soup(url):
        try:
            response = requests.get(url, headers=CoupangCategoryWriter.headers)
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        time.sleep(0.1)

        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        return soup

    def sub_category_parser(self, p_id, p_internal_id, depth=2):
        # 접근 시 페이지 id("data-linkcode")랑 다른 internal_id("data-component-id")써야 함!
        url = f'https://www.coupang.com/np/search/getFirstSubCategory?channel=&component={p_internal_id}'

        soup = self.get_soup(url)

        # 같은 깊이만 탐색
        sub_li_list = [elem for elem in soup.find_all("li")
                       if eval(elem.label["data-coulog"])["depth"] == str(depth)]

        subclasses = {}
        for elem in sub_li_list:

            if elem["data-campaign-id"] != "":
                continue

            children = {}

            category_name = elem.label.text
            category_id = elem["data-linkcode"]  # elem["data-linkcode"]는 웹페이지 링크에서 보임
            internal_category_id = elem["data-component-id"]  # subcategory 접근할 때 필요한 내부 id

            if elem.find("ul", {"class": "search-option-items-child"}):
                children = sub_category_parser(category_id, internal_category_id, depth + 1)

            subclasses[category_id] = {
                "category_name": category_name,
                "internal_category_id": internal_category_id,
                "children": children,
            }

        return subclasses
    # 아래 상수들은 구현 시 수정 가능
    MAX_THREADS = 40

    def second_category_parser(self, parent_category_id):
        # category page link
        url = f'https://www.coupang.com/np/categories/{parent_category_id}'

        target_soup = self.get_soup(url).find("div", {"class": "search-filter-options search-category-component"})
        second_li_list = target_soup.find_all("li")

        second_classes = {}

        for elem in second_li_list:

            # campaign page는 실제 카테고리 분류가 아니기 떄문에 제외함
            if elem["data-campaign-id"] != "":
                continue

            category_name = elem.label.text
            category_id = elem["data-linkcode"]  # elem["data-linkcode"]는 웹페이지 링크에서 보임
            internal_category_id = elem["data-component-id"]  # subcategory 접근할 때 필요한 내부 id

            second_classes[category_id] = {
                "category_name": category_name,
                "internal_category_id": internal_category_id,
                "children": sub_category_parser(category_id, internal_category_id),
            }

        return parent_category_id, second_classes

    def first_category_parser(self):
        # 메인화면에서 긁어올 수 있는 분류는 더보기 때문에 한정되어 있음.
        # 그래서 대분류 별로 페이지에 직접 들어가서 처리해주어야 함.

        # Main page
        url = 'https://www.coupang.com/'

        soup = self.get_soup(url)

        # 최상위 분류
        first_classes = {}

        for first_sub in soup.find("ul", {"class": "menu shopping-menu-list"}).find_all('li', recursive=False):

            # 빈칸일 경우
            if first_sub.a is None:
                continue

            # '패션의류/잡화'는 실제 분류가 아님. 그 밑의 분류를 최상위로 해야 함
            if first_sub.a['href'] == 'javascript:;':
                for first_sub2 in first_sub.find_all('li', {"class": "second-depth-list"}):
                    first_classes[first_sub2.a.get_text(strip=True)] = first_sub2.a['href'][-6:]
            # 나머지 대분류
            else:
                first_classes[first_sub.a.get_text(strip=True)] = first_sub.a['href'][-6:]

        # 대분류 별 하위 페이지로 들어가 하위 분류 모두 탐색

        output_category_structure = {}

        # Multithreading
        threads = min(MAX_THREADS, len(first_classes))

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(second_category_parser, p_id) for p_id in first_classes.values()]

            # tqdm progress bar
            for f in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                c_id, c_children = f.result()

                target_name = list(first_classes.keys())[list(first_classes.values()).index(c_id)]

                output_category_structure[c_id] = {
                    "category_name": target_name,
                    "internal_category_id": "",
                    "children": c_children,
                }

        return output_category_structure

    def to_dict(self):
        pass

    def to_json(self):
        pass


class CoupangCategory:

    @staticmethod
    def verify(category_tree):
        if is_ok(category_tree):
            return True
        else:
            return False

    def __init__(
            self,
            root_category_id='all',
            file_path,
            max_thread=40,
            update=True,
    ):
        cwr = CoupangCategoryWriter(root_category_id, file_path, update)

        if not update and not self.verify(category_tree):
            raise Exception("Check dict: category_tree")
        self.category_tree = category_tree

    def __str__(self):
        tree_str = json.dumps(self.category_tree, indent=4, ensure_ascii=False)
        # json to str
        tree_str = tree_str.replace("\n    ", "\n")
        tree_str = tree_str.replace('"', "")
        tree_str = tree_str.replace(',', "")
        tree_str = tree_str.replace("{", "")
        tree_str = tree_str.replace("}", "")
        tree_str = tree_str.replace("    ", " | ")
        tree_str = tree_str.replace("  ", " ")

        return tree_str

    def __repr__(self):
        return str(self.category_tree)

    def is_exist(self):
        pass

    def get_category_tree(self):
        return self.category_tree

    def get_parent(self):
        pass

    def get_children(self):
        pass







