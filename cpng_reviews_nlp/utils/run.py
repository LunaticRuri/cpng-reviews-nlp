import coupang_data
import pickle
import coupang_reviews_fetcher as cf
from os import listdir
from os.path import isfile, join


def get_part():
    # run!
    # 폴더 구조 잘 보시고 파일이나 폴더가 없으면 에러 나니까 잘 수정해서 받아주세용
    # 파일 없으면 그냥 빈파일 만드시면 되어요.

    work_ch = 'd'  # a, b, c, ..., 작업 단위
    reviews_path = '../../data/dividing/tmp_reviews'  # 리뷰 데이터가 저장될 폴더입니다. 다른 작업 단위랑 겹치면 안돼요.
    completed_set = set([f[:-5] for f in listdir(reviews_path) if isfile(join(reviews_path, f))])

    with open('../../data/dividing/_working/work_' + work_ch + '.pickle', 'rb') as fp:
        tmp_set = set(pickle.load(fp))

    try:
        # 처음에 'err_a.pickle' 이런 식으로 빈파일 만들어 놓으시면 되어요.
        with open('../../data/dividing/err_' + work_ch + '.pickle', 'rb') as fp:
            err_set = set(pickle.load(fp))
    except EOFError:
        err_set = set()

    work_set = tmp_set - completed_set - err_set
    if not work_set:
        print("Done!")
    else:
        crf = cf.CoupangReviewsFetcher(
            work_set,
            reviews_path,
            False,
            40,
            20000,
            work_ch,
        )

        crf.get_reviews()


if __name__ == '__main__':
    get_part()
