import coupang_data
import pickle
import coupang_reviews_fetcher as cf
from os import listdir
from os.path import isfile, join

if __name__ == '__main__':
    # run!
    # coupang_data.fetch_all_reviews()

    work_ch = 'a'  # a, b, c, ...,
    reviews_path = '../data/dividing/tmp_reviews'  # 리뷰 데이터가 저장될 폴더입니다. 다른 작업 단위랑 겹치면 안돼요.
    completed_set = set([f[:-5] for f in listdir(reviews_path) if isfile(join(reviews_path, f))])

    with open('../data/dividing/_completed/completed_' + work_ch + '.pickle', 'wb') as fp:
        pickle.dump(completed_set, fp)

    with open('../data/dividing/_working/work_' + work_ch + '.pickle', 'rb') as fp:
        tmp_set = set(pickle.load(fp))

    try:
        with open('../data/dividing/_err/err_' + work_ch + '.pickle', 'rb') as fp:
            err_set =set(pickle.load(fp))
    except EOFError:
        err_set = set()

    work_set = tmp_set - completed_set - err_set
    if not work_set:
        print("Done!")
    else:
        with open('../data/dividing/_working/work_' + work_ch + '.pickle', 'wb') as fp:
            pickle.dump(work_set, fp)

        crf = cf.CoupangReviewsFetcher(
            work_set,
            reviews_path,
            False,
            40,
            20000,
            work_ch,
        )

        crf.get_reviews()
