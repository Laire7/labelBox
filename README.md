# labelBox
마우스로 박스를 치고 이에 해당 되는 좌표 값들을 불러오기
![image (1)](https://github.com/user-attachments/assets/96862e35-c696-4a37-932a-54bd5259d583)
# 프로그램 기능
0. 파일 목록 읽기(data폴더) *.jpg -> 리스트
1. 이미지 불러오기
2. 마우스 콜백함수 생성
3. 콜백함수 안에서 박스를 그리고, 박스 좌표를 뽑아낸다 (마우스 좌표2개) 참고로 YOLO에서는 박스의 중심좌표(x,y), w, h
4. 이미지 파일명과 동일한 파일명으로 (확장자만 떼고) txt 파일 생성
5. 추가 기능0: 박스를 잘못 쳤을때 'c'를 누르면 현재 파일의 박스 내용 초기화
6. 추가 기능1: 화살표(->)를 누르면 다음 이미지 로딩되고(1~4)
7. 추가 기능2: 박스 좌표들을 txt파일을 만들어서 저장하기 (기존에 txt파일이 있다면 덮어쓰기)
8. 추가 기능3: 화살표(<-)를 눌렀을때 txt파일이 있다면 박스를 이미지 위에 띄워주기
# 사용법
<code> c </code>를 누르면 화면 초기화
<code> 우 화살표 -> </code> 를 누르면 다음 이미지 로딩 
<code> s </code>를 누르면 그린 좌표값들을 (해당 이미지와 동일한 이름을 가진) .txt 파일에 저장. 기존에 txt 파일이 있다면 덮어쓰기
<cdoe> 좌 화살표 <- </code> 를 누르면 (txt 파일에) 저장 된 좌표값들을 이미지 위에 띄워주기
## 함수 목록
* getImageList
* drawRect
* onMouse
* saveLabel
* getLabel
### getImageList
<code>fileDirs = glob(os.path.join(imgFoldr,'*.jpg'))</code>는 폴더 안에 있는 모든 .jpg 이미지들을 불러온다
### drawRect
#### 네모 설정
<code> c = (192, 192, 255) # 원의 색상 (연한 분홍색) </code> 는 마우스로 그리고 저장 할 수 있는 좌표값을 보여준다 <br> 
<code> line_c = (128, 128, 255) # 직선의 색상 (찐한 분홍색) </code> 는 현재 텍스트 파일에 저장 된 좌표값을 보여준다
<code> lineWidth = 2 # 선 두깨 </code> 는 박스의 두깨 값을 지정한다
#### 네모 다시 그리기
<pre><code>
for i in range(0,len(ptList)-1,2):
  cv2.rectangle(cpy, ptList[i], ptList[i+1], color=line_c, thickness=lineWidth)
return cv2.addWeighted(img, 0.3, cpy, 0.7, 0) # 기존 이미지 위에 마우스로 그린 직사각형 종합해서 -> 새로운 이미지로 저장하기   
</code></pre>
for loop과 <code> cv2.addWeighted </code> 을 사용하여, 마우스로 네모를 다시 그릴 때, 마우스를 땔 때까지 예전에 그린 박스도 동시에 볼 수 있다
### onMouse(event, x, y, flags, param)
#### event
1. <code>if event == cv2.EVENT_LBUTTONDOWN:</code>
2. <code>elif event == cv2.EVENT_MOUSEMOVE:</code> 마우스를 움직일 때
  * 마우스의 자표값을 실시간으로 반영하기 위해 기존 이미지를 복사하여 <code> cpy = drawRect(img,cpy, ptList) </code> 를 사용하여 박스 좌표값을 반영한 이미지를 만든다.
  * 마우스의 자표값들이 실시간으로 반영되게 <code> cv2.imshow </code> 함수를 쓴다  
3. <code>elif event == cv2.EVENT_LBUTTONUP:</code> 마우스를 땔 때 (박스를 다 그렸을 때)
  <pre><code>
    if len(ptList)>0: 
      ptList.append((x,y)) 
    if len(ptList)==4:
      del ptList[:-2] 
  </code></pre>
  * <code>del ptList[:-2]</code> 예전에 그렸던 네모와 그의 해당 되는 좌표값들은 지운다
### saveLabel
<code> f.write(newCoor) </code> 함수를 써서 txt 파일 만들거나 덮어쓴다 
<pre><code>        
f = open(txtFile, 'w') # 만약 파일이 있으면, 덮어쓰기
newCoor = str(list(map(lambda x: ptList[x], range(0,2))))
print(f'Label with coordinates {newCoor} saved to file {txtFile}')
f.write(newCoor) # txt 파일에 새로운 좌표값들을 받아쓰기
f.close() # 파일들이 RAM에 쌓이지 않게, 파일을 꼭 닫기!
</code></pre>
#### getLabel
<code> line = f.readline() </code> 를 활용하여 txt 파일에 저장된 좌표값을 불러온다
* 좌표값 포맷은 [(),()] 한 목록 list 안에 처음 마우스를 누른 좌표 값과 마우스를 땐 좌표 값 각각 2개 포인트를 튜플 값을 저장한다
#### main
1. <code>imgList = getImageList()</code>함수를 사용하여 폴더 안에 이미지들을 불러온다
2. <code>cv2.namedWindow('label')</code>마우스를 추적 할 수 있는 창을 만들고 난 뒤 이미지를 읽고 화면에 띄운다
  <pre><code> 
  img = cv2.imread(imgList[imgId]) # 이미지 불러오기
  cv2.imshow('label', img)
  </code></pre>
3. while loop안에 각 함수들을 불러온다
  1. <code>cv2.setMouseCallback('label', onMouse)</code> 마우스의 움직임과 <code> key = cv2.waitKeyEx() </code> 키보드 입력을 계속 추적한다
  2. if elif 문장 안에 다음과 같은 키보드 입력들에 해당 되는 함수들을 불러온다
  * <code>c</code>화면 초기화
    <pre><code>
    if key == ord('c'):
      ptList.clear()
      cv2.imshow('label', img)  
    </code></pre>
  * <code> 우 방향키 -> </code> 다음 이미지 로딩
    <pre><code>
    elif key== 0x270000:
      imgId = (imgId+1)%len(imgList) # 파일 목록에 끝에 도달했으면 다시 첫번째 파일로 돌아가기
      cv2.destroyAllWindows()
      cv2.namedWindow('label') # 마우스 움직임을 추적할 수 있는 창 만들기
      break
    </code></pre>
  * <code>s</code> 좌표값 저장
    <pre><code>
    elif key == ord('s'):
      saveLabel(ptList, imgList[imgId])
    </code></pre>
  * <code> 우 방향키 -> </code> 저장 된 자표값들을 이미지 위에 띄어주기
    <pre><code>
    elif key== 0x250000:
      ptList = getLabel(imgList[imgId])
      if ptList is not None:
        cpy = drawRect(img, img.copy(), ptList, True) # 새로운 좌표를 반영한 이미지를 만들어서
        cv2.imshow('label',cpy) # 실시간으로 변해가는 네모 좌표를 화면에 띄우기
    </code></pre> 
