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
# 추가 기능2: 그린 박스 좌표들을 txt파일을 만들어서 저장하기 (기존에 txt파일이 있다면 덮어쓰기)
# 추가 기능3: 화살표(<-)를 눌렀을때 txt파일이 있다면 박스를 이미지 위에 띄워주기 

# YOLO
# def 
#     x_center =
#     y_center =
#     width =
#     height = 
#############################################################################################################################
#### 함수 정의 ####
### 1. 해당 폴더 안에 저장 된 모든 이미지들 불러오기
# return : io.Textfile 집합한 배열
def getImageList():
    baseDir = os.getcwd() # 현재 작업 directory 확인
    imgFoldr = os.path.join(baseDir,'images/') # 이미지들이 저장된 폴더 확인하기
    fileDirs = glob(os.path.join(imgFoldr,'*.jpg')) # 폴더 안에 있는 모든 이미지들을 불러오기
    
    return fileDirs


### 추가 기능 2: 파일에 저장된 좌표 값들을 읽어오기
# return : 파일에서 읽어온 좌표값들을 숫자로 된 튜플 배열 값으로 반환
def getPts(txtFile, line):
    ## 변수 목록
    # 전역 변수 
    global savPtDict # 파일에 저장 된 좌표 값을 화면에 띄우기 위해 전역 변수로 저장하기
    # 지역 변수
    numList = [] # 파일 안에 문자열을 -> 숫자 값으로 저장하기
    num = '' # 문자열을 -> 숫자로 변경하기 위한 변수 값
    
    ## 문자열 -> 숫자 좌표 값들로 변경하기 
    for i in range(2,len(line)-2): # 배열의 괄호 건너뛰어 파일에서 좌표 값들 가지고 오기
        if(line[i].isdigit()):
            num +=line[i] 
        if(not line[i+1].isdigit() and num): # 각 좌표 값의 숫자 길이를 측정하기 위해
            numList.append(int(num)) # 문자열로 쓰여 있는 숫자를 나중에 그리기 편한 정수 값으로 변경해서 저장하기
            num = '' # 한 숫자가 끝나고, 새로운 숫자를 읽어오기 위해
    
    return list(tuple(numList[0:2]),tuple(numList[1:3]))


### 2. 마우스 콜백함수 생성
# return: 없음
def onMouse(event, x, y, flags, param):
    ## 변수 목록
    # 전역 변수
    global ptList, img, cpy, key, running  
    # 지역 변수 
    cpy = img.copy() 
    
    ## 마우스 움직임을 화면에 반영하기
    # 마우스 좌 클릭으로 네모의 (두 개 중) 첫 번째 좌표를 지정해서
    if event == cv2.EVENT_LBUTTONDOWN:
        ptList.append((x,y)) # 새로 그리는 좌표를 전역 변수 목록에 저장하기
    
    # 마우스가 실시간으로 가르키는 두번째 좌표 가지고 네모 그리기 (마우스 좌 클릭으로 네모의 첫번째 좌표를 지정한 후)
    elif event == cv2.EVENT_MOUSEMOVE: 
        if len(ptList)==3 or len(ptList)==1: # 그릴 네모(들)의 첫번째 좌표를 지정했는지 확인 (새로 그린 네모를 지정하기 전에 직전에 그린 네모도 볼 수 있게)
            ptList.append((x,y)) # 새로운 좌표를 전역 변수에 저장하고 
            cpy = drawROI(cpy, ptList) # 새로운 좌표를 반영한 이미지를 만들어서
            cv2.imshow('label',cpy) # 실시간으로 변해가는 네모 좌표를 화면에 띄우지만
                       
            # 사용자가 현재 그리는 네모를 저장하고 싶은지 확인 
            if (key!=ord('s')): 
                ptList.pop() # 마우스 왼쪽 버튼을 때서 새로운 네모를 지정 할 때 까지는 네모의 두번째 좌표를 저장되지 않도록 전역 배열에서 지운다
            else:
                savLabel()
    
    # 마우스를 땔 때 네모의 두 번째 좌표를 임시적으로 저장하고, 전에 그려낸 네모가 있으면 지우기   
    elif event == cv2.EVENT_LBUTTONUP: 
        if len(ptList)>0: # (좌 클릭 후) 새로 네모를 그리는 중에 화면을 백지화 하는 경우, 네모가 좌 클릭으로 두 번째 좌표를 지정하는 것을 막기 위해 
            ptList.append((x,y)) 
        if len(ptList)>3: # 네모가 두 개 이상 지정 되는 것을 방지 하기 위해
            del ptList[0:2] # 새로운 네모를 지정한 후, 예전에 지정한 네모가 있으면 지우고       
        cpy = drawROI(cpy, ptList) # 새로 지정한 네모만 화면에 띄우기 위해 새로 이미지 지정하기  
        cv2.imshow('label', cpy)


### 3. 콜백함수 안에서 박스를 그리고, 박스 좌표를 뽑아낸다 (마우스 좌표2개)
## 직사각형은 마우스로 지정한 두 좌표 값들 (ptList 전역 변수로) 그리기
# return : 기존 이미지 위에 마우스로 그린 직사각형을 종합한 새로운 이미지 반환 
def drawROI(img, ptList, dispSaved=False):
    ## 변수 목록
    # 전역 변수
    global cpy # 저장 혹은 예전에 그린 레이블이 있는지 확인하기 위해
    
    ## 변수 정의
    if not cpy: # 만약  
        cpy = img.copy() # 레이블을 그려낼 레이어를 새로 생성하기
    # deep copy : 이미지 복사해서 레이어를 하나 추가 (가이드 라인과 모서리 폰이트를 추가로 그려주는)
    
    # 그려낼 네모의 컬러와 두깨 지정
    if not dispSaved: # 저장 된 좌표값들은 색깔로 구분하기
        c = (192, 192, 255) # 원의 색상 (연한 분홍색)
        line_c = (128, 128, 255) # 직선의 색상 (찐한 분홍색)
        lineWidth = 2 # 선 두깨
    else: 
        c = (101, 147, 245) # 원의 색상 (연한 파랑색)
        line_c = (25, 25, 112) # 직선의 색상 (밤 하늘 색)
        lineWidth = 3 # 선 두깨
    
    # 사용자가 지정한 좌표값에 따라 레이블 직사각형 그리기
    for i in range(0,len(ptList)-1,2): # 사용자가 새 레이블 값을 지정하기 전까지 예전에 그린 레이블 좌표값들을 표시하기
        cv2.rectangle(cpy, ptList[i], ptList[i+1], color=line_c, thickness=lineWidth)
    cpy = cv2.addWeighted(img, 0.3, cpy, 0.7, 0) # 기존 이미지 위에 마우스로 그린 직사각형 종합해서 -> 새로운 이미지로 저장하기     
    # addWeight 파라미터: 첫 번째 종합 할 이미지 alpha=0.3, 두번째 종합 할 이미지 beta=0.7, gamma=0 ?????????????
    
    return cpy


### 4. 이미지 파일명과 동일한 파일명으로 (확장자만 떼고) txt 파일 생성
# return : 없음
def savLabel():
    ## 변수 목록
    # 전역 변수 
    global ptList # 저장 할 좌표 값을 불러오기
    
    # ## 좌표값을 txt 파일에 저장하기
    # # Case 1. 먼저 저장 할 네모가 있는지 (두 좌표가 지정 되었는지)확인
    # if(len(ptList)>1):
        
    # Case 2. 두 네모가 화면에 띄어 있는지 확인
    if(len(ptList)>2):
        # 사용자가 (둘 중) 어떤 네모를 저장하고 싶은지 지정 할 때까지 사용자 입력 기다리기 (이 와중에 사용자가 프로그램 종료도 명시 할 수 있다는 점도 고려 함)
        chooseLabel = None # 사용자 입력 변수
        while(not(chooseLabel == '1' or chooseLabel == '2')):
            chooseLabel = input(f"Do you wish to save the coordinates of the first(1) or second(2) rectangle? Please press 1 or 2 (or press 'q' to quit program):") #입력 값은 문자열로 저장
            if(chooseLabel=='q'): # 사용자가 프로그램 종료를 명시 할 경우
                running = False # 모든 반복문에서 빠져 나오고 프로그램을 종료 하기 위해
                break # 그리고 현재 들어가 있는 반복문에 빠져나오기
        
        # txt 파일에 첫번째 아니면 두번째 그린 네모를 저장할지 지정
        if(chooseLabel=='1'):                    
            print(f'First (1) ', end='')  
        elif(chooseLabel=='2'):
            del ptList[2:4] # 전에 그렸던 레이블 좌표들 지우기
            print(f'Second (2) ', end='')
        
    # 해당 레이블 좌표값들을 txt 파일에다가 저장하기 
    if(running): # 프로그램 종료를 명시 했는지 확인
        # txt 파일을 새로 생성하기
        imgFileName, ext = os.path.splitext(imgDirs[0]) # 좌표값을 저장 할 텍스트 파일은 화면에 띄운 이미지와 유사한 이름과 directory가지고 있다
        txtFile = imgFileName + '.txt'
        f = open(txtFile, 'w') # 만약 파일이 있으면, 덮어쓰기
        
        # 새로운 좌표 값들을 구현하고 프로그램 전역 변수에 저장하기
        print(f'Label with coordinates {str(list(tuple(ptList[0]), tuple(ptList[1])))} saved to file {txtFile}')
        
        # txt 파일에 새로운 좌표값들을 받아 쓰고 닫기
        f.write(str(list(tuple(ptList[0]), tuple(ptList[1]))))
        f.close()
    
    # # 새로 저장 할 좌표값들이 없으면     
    # else:
    #     print(f'No label to save! Please indicate the coordinates you want to save by (clicking and dragging) with your mouse')


### 추가 기능0: 박스를 잘못 쳤을때 'c'키를 누르면 현재 파일의 박스 내용 초기화
def clearBoard():
    ## 변수 목록
    # 전역 변수
    global ptList, toggleDisp # 그렸던 모든 좌표들 지우기
    
    ## 변수 정의
    ptList.clear()
    dispSaved = False
    
    cpy = img.copy() # 원본 이미지 복사해서 화면에 띄우기
    cv2.imshow('label', cpy)
    
#### 전역 변수들 정의 ####
### 이미지 파일과 관련 하여
imgId = 0 # 어떤 이미지 파일을 화면에 띄우는지 지정
imgDirs = getImageList() # 이미지 파일들을 불러오기
### 좌표 값과 관련 하여
ptList = [] # 화면에 띄울 좌표들 (저장 한 좌표 외에) 
### 좌표 값 지정 후 보여 줄 화면 (기존 이미지 위와 종합해서 보여주기)
cpy = None         
### 프로그램 종료와 관련 하여
running = True # 반복문을 빠져나와 프로그램을 종료 할지 지정 
key = cv2.waitKey() # 프로그램 실행 중, 언제든지 사용자 프로그램을 종료 하거나 작업 한 것을 저장 할 수 있게끔 항상 키 입력 대기하기 ('q')

# 프로그램을 실행 할 화면 지정하기
cv2.namedWindow('label') # 띄울 화면 지정하기


#### 프로그램 실행 (종료를 'q' 키로 명시하기 전까지 프로그램을 계속 실행) ####
### 첫번째 반복문은 이에 해당 될 때만 실행 된다:
## 1. 처음 프로그램을 실행 하기 위해 화면을 새로 띄우기
## 2. 오른쪽 방향키를 (->) 눌러 새로운 이미지를 불러오기 위해
### 두번째 반목에 추가 기능들 넣었음
## (맨 위에 프로그램 기능 소개 글과 동일함)
## 추가 기능0: 박스를 잘못 쳤을때 'c'키를 누르면 현재 파일의 박스 내용 초기화
## 추가 기능1: 화살표(->)를 누르면 다음 이미지 로딩되고(1~4)
## 추가 기능2: 그린 박스 좌표들을 저장하기 위해 's'키를 누르면 txt파일을 만들어서 저장하기 (기존에 txt파일이 있다면 덮어쓰기)
## 추가 기능3: 화살표(<-)를 눌렀을때 txt파일이 있다면 박스를 이미지 위에 띄워주기 

### 첫번째 반복문 : 기존에 작업한 거 다 지우고 새로 작업 할 이미지 띄우기
while running:
    ## 레이블링 작업을 진행 할 이미지 불러오고
    img = cv2.imread(imgDirs[imgId]) 
    ## 기존에 그렸던 모든 작업들 싹 다 지우기
    ptList.clear()
    cpy = img.copy()
    cv2.imshow('label', cpy) # (아무것도 그려지지 않은) 이미지를 화면에 띄우기
    
    ### 두번째 반복문 : 레이블링 작업 실행
    while running:
        ## 언제든지 사용자가 프로그램을 지정 할 수 있게, 항상 키와 마우스 입력 대기 
        cv2.setMouseCallback('label', onMouse, cpy) # 마우스 움직임을 읽고 화면에 반영하기 
        
        ##-1. 프로그램 종료를 명령 했는지 확인하기 
        if key==ord('q'): # ord는 'q'에 해당 되는 ascii 값을 불러와서 
            running = False # 프로그램이 더 이상 실행 되지 않게 모든 반복문을 멈추기
            break # 먼저 해당 (두 반복문 중에 두 번째) 반복문에서부터 빠져나오기 
        
        ## 추가 기능0: 이미지 위에 그려진 모든 좌표 값들 지우기
        elif key==ord('c'):
            cpy = clearBoard(cpy, ptList)
        
        ## 추가 기능1: 우 방향키 (->)를 누르면 다음 이미지 로딩하기(1~4)
        elif key== 0x270000:
            f = (f+1)%len(imgDirs) # 파일 목록에 끝에 도달했으면 다시 첫번째 파일로 돌아가기
            break                  
        
        ## 추가 기능2: 새로 그렸거나 그리고 있는 네모를 저장하기 
        elif key==ord('s'):
            # 먼저 저장 할 레으블이 있는지 확인
            if(len(ptList)>1):
                savLabel(ptList) 
            else:
                print(f'No label to save! Please indicate the coordinates you want to save by (clicking and dragging) with your mouse')
        
        ## 추가 기능3: 화살표(<-)를 눌렀을때 txt파일이 있다면 박스를 이미지 위에 띄워주기

        elif key == 0x250000:
            # txt파일로 저장한 좌표값이 있는지 확인
            txtFile = os.path.splitext(imgDirs[0]) + '.txt'
            if(os.path.exists(txtFile)): 
                readFile = open(txtFile, 'r').read()
                savPts = getPts(txtFile, readFile) # txt 파일에 저장한 좌표값들을 불러와서
                dispSaved = True
                
                if(dispSaved): 
                    #txt 파일에 저장한 좌표값을 화면에 띄우기                    
                    cpy = drawROI(cpy, ptList, dispSaved=True) # 저장한 좌표값들을 화면에 추가하여
                else:
                    cpy = drawROI(cpy, ptList, dispSaved=False)
                cv2.imshow('label',cpy)  
                cv2.setMouseCallback('label', onMouse, cpy)
                
                dispSaved = not dispSaved  # 왼쪽 화살표를 한번 더 누르면 저장 된 좌표 다시 숨기기 위해       
            else:
              print("No label coordinates saved for the corresponding image!") 

#### 모든 창들 닫고 프로그램 종료 ####
print('Exiting out of the program')     
cv2.destroyAllWindows()