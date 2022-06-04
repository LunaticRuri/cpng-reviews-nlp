# 구동 방법

이 폴더에 model 폴더 생성하고, 모델 데이터(pickle) 저장

패키지 의존성 

cpng_nlp_viz 폴더 전체를 서버 쪽으로 옮겨서

작동 예시
$ nohup bokeh serve cpng_nlp_viz --num-procs --address== 0.0.0.0 --allow-websocket-origin=13.209.52.34:5006 &

포트 오픈 보안 정책 유의하기

