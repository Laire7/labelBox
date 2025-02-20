import cv2, os, sys
import numpy as np
from glob import glob

# 0. 파일 목록 읽기(data폴더) *.jpg -> 리스트
# 1. 이미지 불러오기
# 2. 마우스 콜백함수 생성
# 3. 콜백함수 안에서 박스를 그리고, 박스 좌표를 뽑아낸다 (마우스 좌표2개)
#    참고로 YOLO에서는 박스의 중심좌표(x,y), w, h
# 4. 이미지 파일명과 동일한 파일명으로 (확장자만 떼고) txt 파일 생성
# 추가 기능0: 박스를 잘못 쳤을때 'c'를 누르면 현재 파일의 박스 내용 초기화
# 추가 기능1: 화살표(->)를 누르면 다음 이미지 로딩되고(1~4)
# 추가 기능2: 박스 좌표들을 txt파일을 만들어서 저장하기 (기존에 txt파일이 있다면 덮어쓰기)
# 추가 기능3: 화살표(<-)를 눌렀을때 txt파일이 있다면 박스를 이미지 위에 띄워주기

#! 함수 정의 
# 0. 파일 목록 읽기(data폴더) *.jpg -> 리스트
# return : io.Textfile 집합한 배열
def getImageList():
    baseDir = os.getcwd() # 현재 작업 directory 확인
    imgFoldr = os.path.join(baseDir, 'opencvDojang\\images\\') # 이미지들이 저장된 폴더로 directory 정의하기
    print(imgFoldr)
    fileDirs = glob(os.path.join(imgFoldr,'*.jpg')) # 폴더 안에 있는 모든 이미지들을 불러오기
    return fileDirs

# 네모 그리기            
def drawRect(img, cpy, ptList, saved=False):
    # 그려낼 네모의 컬러와 두깨 지정
    c = (192, 192, 255) # 원의 색상 (연한 분홍색)
    line_c = (128, 128, 255) # 직선의 색상 (찐한 분홍색)
    lineWidth = 2 # 선 두깨
    if saved: # 저장 된 좌표는 다른 색으로 표현하기
        c = (101, 147, 245) # 원의 색상 (연한 파랑색)
        line_c = (25, 25, 112) # 직선의 색상 (밤 하늘 색)
        lineWidth = 3 # 선 두깨
    
    # 사용자가 지정한 좌표값에 따라 레이블 직사각형 그리기
    for i in range(0,len(ptList)-1,2):
        cv2.rectangle(cpy, ptList[i], ptList[i+1], color=line_c, thickness=lineWidth)
    return cv2.addWeighted(img, 0.3, cpy, 0.7, 0) # 기존 이미지 위에 마우스로 그린 직사각형 종합해서 -> 새로운 이미지로 저장하기   
    
# 3. 콜백함수 안에서 박스를 그리고, 박스 좌표를 뽑아낸다 (마우스 좌표2개)
def onMouse(event, x, y, flags, param):
    #! 변수 정의
    global ptList, img
    cpy = img.copy()

    # ! 마우스 움직임에 따라 좌표 그리기
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(ptList)==0 or len(ptList)==2:
            ptList.append((x,y)) # 새로 그리는 좌표를 전역 변수 목록에 저장하기
    
    # Click and drag으로 마우스가 실시간으로 가르키는 두번째 좌표 가지고 네모 그리기 (마우스 좌 클릭으로 네모의 첫번째 좌표를 지정한 후)
    elif event == cv2.EVENT_MOUSEMOVE: 
        if len(ptList)==1 or len(ptList)==3: # 그릴 네모(들)의 첫번째 좌표를 지정했는지 확인 (새로 그린 네모를 지정하기 전에 직전에 그린 네모도 볼 수 있게 두 조건을 줬다)
            ptList.append((x,y)) # 새로운 좌표를 전역 변수에 저장하고
            cpy = drawRect(img,cpy, ptList) # 새로운 좌표를 반영한 이미지를 만들어서
            cv2.imshow('label',cpy) # 실시간으로 변해가는 네모 좌표를 화면에 띄우기
            ptList.pop() # 마우스를 띄우지 않은면, 좌표 지우기
    
    # 마우스를 땔 때 네모의 두 번째 좌표를 임시적으로 저장하고, 전에 그려낸 네모가 있으면 지우기   
    elif event == cv2.EVENT_LBUTTONUP: 
        if len(ptList)>0: # (좌 클릭 후) 새로 네모를 그리는 중에 화면을 백지화 하는 경우, 네모가 좌 클릭으로 두 번째 좌표를 지정하는 것을 막기 위해
            ptList.append((x,y)) # 새로운 좌표를 전역 변수에 저장하고
            if len(ptList)==4:
                del ptList[:-2] # 새로운 네모를 지정한 후, 예전에 지정한 네모가 있으면 지우기       
            cpy = drawRect(img, cpy, ptList)
            cv2.imshow('label',cpy)
            

# 4. 이미지 파일명과 동일한 파일명으로 (확장자만 떼고) txt 파일 생성
def saveLabel(ptList, imgPath):   
    #! 현황 파악하기
    # Bad Case 1. 먼저 저장 할 네모가 있는지 (두 좌표가 지정 되었는지)확인
    if (len(ptList)<2):
        print(f'At least two coordinates needed. Please indicate the coordinates you want to save by clicking, dragging, and lifting your mouse')
    else:
        #! 해당 레이블 좌표값들을 txt 파일에다가 저장하기 
        # 1. txt 파일을 이름 지정하기
        imgFileName, ext = os.path.splitext(imgPath) # 좌표값을 저장 할 텍스트 파일은 화면에 띄운 이미지와 유사한 이름과 directory가지고 있다
        txtFile = imgFileName + '.txt'
        print("txtFile " + txtFile)
        # 2. txt 파일 만들기
        f = open(txtFile, 'w') # 만약 파일이 있으면, 덮어쓰기
        newCoor = str(list(map(lambda x: ptList[x], range(0,2))))
        print(f'Label with coordinates {newCoor} saved to file {txtFile}')
        f.write(newCoor) # txt 파일에 새로운 좌표값들을 받아쓰기
        f.close() # 파일들이 RAM에 쌓이지 않게, 파일을 꼭 닫기!

# 5. 해당 이미지를 위한 좌표값들을 가지고 오기
def getLabel(imgPath):
        #1. 해당 이미지를 위한 txt 파일 열기
        imgFileName, ext = os.path.splitext(imgPath) # 좌표값을 저장 할 텍스트 파일은 화면에 띄운 이미지와 유사한 이름과 directory가지고 있다
        txtFile = imgFileName + '.txt'
        #2. txt 파일 안에 저장된 좌표값들을 불러오기
        if os.path.isfile(txtFile):
            f = open(txtFile, 'r')
            line = f.readline()  # Read the first line of the file
            f.close()
            #3. 자표값들을 숫자 목록으로 바꾸기
            ptList = eval(line)
            print("ptList")
            print(ptList)
            # num_list = [int(num) for num in ''.join([char if char.isdigit() or char == ',' else '' for char in line]).split(',') if num]
            # ptList = [(num_list[i], num_list[i + 1]) for i in range]
            return ptList
        else:
            print("No labels saved for this image") 
            return None


#! 메인 함수 샐행
if __name__ == "__main__":
    #! 변수 정의 
    imgList = getImageList() 
    
    if not imgList:
        print("No images found in the 'images/' directory.")
        sys.exit()
    
    imgId = 0 # 이미지 파일 지정
    ptList = [] # 박스 좌표 목록
    saving = False # 사용자가 그리는 도중, 좌표를 저장하고 싶을 때
    cv2.namedWindow('label') # 마우스 움직임을 추적할 수 있는 창 만들기 
    
    #! 프로그램 실행 반복문
    running = True # 프로그램 종료 변수
    
    while running:
        #셋업
        ptList.clear()
        # 1. 이미지 불러오기
        img = cv2.imread(imgList[imgId]) # 이미지 불러오기
        cv2.imshow('label', img)
        
        #! 새로운 이미지 띄우고 난 후, 좌표 그리기 반복문
        while running:
            # 2. 마우스 콜백함수 생성
            cv2.setMouseCallback('label', onMouse) # 마우스 움직임을 추적하기              
            
            #! 추가 기능 설정
            key = cv2.waitKeyEx() # 프로그램 실행 명렁어들을 키보드로 입력
            # 추가 기능0: 박스를 잘못 쳤을때 'c'를 누르면 현재 파일의 박스 내용 초기화
            if key == ord('c'):
                ptList.clear()
                cv2.imshow('label', img)
            
            # 추가 기능1: 우 방향키 (->)를 누르면 다음 이미지 로딩하기(1~4)
            elif key== 0x270000:
                imgId = (imgId+1)%len(imgList) # 파일 목록에 끝에 도달했으면 다시 첫번째 파일로 돌아가기
                cv2.destroyAllWindows()
                cv2.namedWindow('label') # 마우스 움직임을 추적할 수 있는 창 만들기
                break
            
            # 추가 기능2: 그린 박스 좌표들을 txt파일을 만들어서 저장하기 (기존에 txt파일이 있다면 덮어쓰기)
            elif key == ord('s'):
                saveLabel(ptList, imgList[imgId])
                
            # 추가 기능3: 좌 방향키 (<-) 눌렀을때 txt파일이 있다면 박스를 이미지 위에 띄워주기
            elif key== 0x250000:
                ptList = getLabel(imgList[imgId])
                if ptList is not None:
                    cpy = drawRect(img, img.copy(), ptList, True) # 새로운 좌표를 반영한 이미지를 만들어서
                    cv2.imshow('label',cpy) # 실시간으로 변해가는 네모 좌표를 화면에 띄우기
            else:
                running = False

#### 모든 창들 닫고 프로그램 종료 ####
print('Exiting out of the program')   
cv2.destroyAllWindows()

