# ETRI SCEngine Prototype

ETRI 엔진 도커를 위한 구조

## 개발 환경
- 데이터 폴더는 항상 고정된 위치에 있는 것으로 가정
  ```python
  # 컨테이너 내부에 항상 고정된 위치에 폴더 위치
  # 도커로 실행시 volume binding으로 호스트의 폴더를 연결
  SCENE_DIR = "./Data"
  INPUT_DIR = "./Input"
  OUTPUT_DIR = "./Output"
  ```
- `INPUT_DIR`, `OUTPUT_DIR`은 엔진에 자료입출력을 위한 폴더
  * `INPUT_DIR`에는 이미지파일만 존재해야함
- `SCENE_DIR`은 내부 데이터 구조

- SC영상 및 동영상을 이용한 프로그램 실행 및 테스트
  ```shell
  # $INPUT_DIR에 있는 이미지파일들을 $SCENE_DIR에 복사. $OUTPUT_DIR에 영상 및 동영상 정보가 info.json파일로 저장됨.
  $ python run_init.py 
  
  # colmap을 돌려서 그 결과를 $SCENE_DIR에 저장. frame_number의 디폴트 값은 0.
  $ python run_build_param.py --frame_number 1
  
  # make_layer를 수행. factor는 이미지 사이즈를 얼마나 줄일지를 결정. 여기의 factor숫자의 비율로 줄임. 4K (3840 x 2160)의 영상일 경우 factor가 4일경우 (960 x 540)으로 줄임. frame_number의 디폴트 값은 0.
  $ python run_build_layer.py --factor 4 --frame_number 1
  
  # 렌더링 수행. view_range는 어느정도의 범위에서 렌더링을 수행할지, focal은 기준점이 어디인지, num_views는 생성하는 렌더링영상이 몇개인지, result는 결과가 저장될 폴더가 어디인지를 나타냄. $OUTPUT_DIR폴더에 저장됨. frame_number의 디폴트 값은 0. save_viewing옵션을 넣으면, 뷰파라미터가 $OUTPUT_DIR폴더에 param.json파일로 저장됨.
  $ python run_render.py --view_range 1.0 --focal 50 --num_views 49 --frame_number 1 --save_viewing
  
  # 퀼트영상 생성. run_render.py와 비슷한데, 생성되는 영상 개수대신 퀼트영상의 rows와 cols를 입력받고, $OUTPUT_DIR 아래에 res_qs{rows}x{cols}.png파일로 저장됨. frame_number의 디폴트 값은 0.
  $ python run_render_quilt.py --view_range 1.0 --focal 50 --rows 7 --cols 7 --frame_number 1
  ```

## 도커 이미지 빌드

- 파워쉘에서 다음 명령어로 이미지 생성 및 도커허브로 이미지 전송(push)
  ```shell
  $ docker buildx build --push --platform linux/amd64 --tag devboxhq/npo:etri_scapi-$VERSION .
  ```
- 사전에 `docker login`으로 도커 로그인 수행


## 도커를 이용한 엔진 실행

- 다음 명령어로 컨테이너 실행
- volume binding을 이용해 `data`폴더를 컨테이너와 연결
- 영상의 경우 실행방법 (frame_number옵션을 생략한다. 즉, frame_number를 0으로 간주한다.)

  ```shell
  $ docker run --gpus all -it --rm -v ./Sample:/etri_workspace/Data -v ./Output:/etri_workspace/Output -v ./Input:/etri_workspace/Input devboxhq/npo:etri_scapi-$VERSION python run_init.py
  $ docker run --gpus all -it --rm -v ./Sample:/etri_workspace/Data devboxhq/npo:etri_scapi-$VERSION python run_build_param.py
  $ docker run --gpus all -it --rm -v ./Sample:/etri_workspace/Data devboxhq/npo:etri_scapi-$VERSION python run_build_layer.py --factor 4
  $ docker run --gpus all -it --rm -v ./Sample:/etri_workspace/Data -v ./Output:/etri_workspace/Output devboxhq/npo:etri_scapi-$VERSION python run_render.py --view_range 1.0 --focal 50 --num_views 49 --save_viewing
  $ docker run --gpus all -it --rm -v ./Sample:/etri_workspace/Data -v ./Output:/etri_workspace/Output devboxhq/npo:etri_scapi-$VERSION python run_render_quilt.py --view_range 1.0 --focal 50 --rows 7 --cols 7
  ```
- 동영상의 경우 실행방법
  * 아래 샘플의 경우 ./VideoSample폴더에는 영상파일들만 들어가고, 그 영상파일들을 몇번 프레임폴더에 넣을지를 결정함
  ```shell
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data -v ./Input:/etri_workspace/Input -v ./Output:/etri_workspace/Output devboxhq/npo:etri_scapi-$VERSION python run_init.py 

  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data devboxhq/npo:etri_scapi-$VERSION python run_build_param.py  # 0번 프레임 데이터로 colmap실행

  # 0번 프레임
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data devboxhq/npo:etri_scapi-$VERSION python run_build_layer.py --factor 4
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data -v ./Output:/etri_workspace/Output npo:etri_scapi-$VERSION python run_render.py --view_range 1.0 --focal 50 --num_views 49 --save_viewing
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data -v ./Output:/etri_workspace/Output npo:etri_scapi-$VERSION python run_render_quilt.py --view_range 1.0 --focal 50 --rows 7 --cols 7 

  # 1번 프레임
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data devboxhq/npo:etri_scapi-$VERSION python run_build_layer.py --factor 4 --frame_number 1
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data -v ./Output:/etri_workspace/Output npo:etri_scapi-$VERSION python run_render.py --view_range 1.0 --focal 50 --num_views 49 --save_viewing --frame_number 1
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data -v ./Output:/etri_workspace/Output npo:etri_scapi-$VERSION python run_render_quilt.py --view_range 1.0 --focal 50 --rows 7 --cols 7 --frame_number 1

  # 2번 프레임
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data devboxhq/npo:etri_scapi-$VERSION python run_build_layer.py --factor 4 --frame_number 2
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data -v ./Output:/etri_workspace/Output npo:etri_scapi-$VERSION python run_render.py --view_range 1.0 --focal 50 --num_views 49 --save_viewing --frame_number 2
  $ docker run --gpus all -it --rm -v ./VideoSample:/etri_workspace/Data -v ./Output:/etri_workspace/Output npo:etri_scapi-$VERSION python run_render_quilt.py --view_range 1.0 --focal 50 --rows 7 --cols 7 --frame_number 2
  ```

