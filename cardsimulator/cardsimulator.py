
import requests
from bs4 import BeautifulSoup
import pickle
import tkinter as tk
from tkinter import ttk
from PIL import Image
import os
import re
import random
import copy
from pathlib import Path
import sys



#this version is 0.0.5

#更新記録
#v0.0.1 基礎部分を設計
#v0.0.2 転醒部分を実装
#v0.0.3 デッキに戻す部分を実装
#v0.0.4 極軽減、全軽減に適応
#v0.0.5 入力部が不親切だったので改定



##----------------------------------------------------------------------------------------------
##ここからコード↓

CARD_WIDTH = 105
CARD_HEIGHT = 153
BUTTON_WIDTH = 105
BUTTON_HEIGHT = 31

#pyinstaller用の関数
# アクセスしたいファイル名(同フォルダ内)を引数に渡すと絶対パスを返す
def find_data_file(filename):
   if getattr(sys, "frozen", False):
       # The application is frozen
       datadir = os.path.dirname(sys.executable)
   else:
       # The application is not frozen
       # Change this bit to match where you store your data files:
       datadir = os.path.dirname(__file__)
   return os.path.join(datadir, filename)

#外部処理関数
def contenthtml(url):
    html = requests.get(url)
    return BeautifulSoup(html.content, "html.parser")
    #print ("contenthtml END")

def searchcardlist(name,cash):
    contentnumber = 0
    for card in cash:
        if name == card[0]:
            return contentnumber
        else:
            contentnumber+=1
    return -1
    #print ("searchcardlist END")

def reductionarray(detail):
    colorsum = []
    try:
        for colors in detail.find_all('img'):
            color = colors.get('src')
            if('red' in color):
                colorsum.append("赤")
            elif('green' in color):
                colorsum.append("緑")
            elif('pup' in color):
                colorsum.append("紫")
            elif('white' in color):
                colorsum.append("白")
            elif('yellow' in color):
                colorsum.append("黄")
            elif('blue' in color):
                colorsum.append("青")
            elif('ultimate' in color):
                colorsum.append("極")
            elif('all' in color):
                colorsum.append("全")
            else:
                colorsum = []
    except:
        colorsum = []
    return colorsum
    #print ("reductionarray END")

def createarray(content,number,array):
    img = content.find(True, attrs={ 'class': 'set' }).find(True, attrs={ 'class': 'img' }).find('img')
    laterurl = img.get('src')
    imgurl = "https://club.battlespirits.com" + laterurl
    try:
        with open(find_data_file(str('./cardcash/')+number+str('.jpg')),'wb') as file:
            file.write(requests.get(imgurl).content)
    except OSError as e:
        os.mkdir(find_data_file('./cardcash'))
        with open(find_data_file(str('./cardcash/')+number+str('.jpg')),'wb') as file:
            file.write(requests.get(imgurl).content)
    finally:
        imgjpg = Image.open(find_data_file(str('./cardcash/')+number+str('.jpg')))
        imgjpg.save(find_data_file(str('./cardcash/')+number+str('.png')))
        os.remove(find_data_file(str('./cardcash/')+number+str('.jpg')))
    array.append(number)
    array.append(content.find(True,attrs={ 'class': 'name' }).text)
    for detail in content.find(True,attrs={ 'class': 'data' }).find_all(True,attrs={ 'class': 'txt' }):
        if(detail.text==''):
            array.append(reductionarray(detail))
        else:
            array.append(detail.text)
    leveltext = ''
    for line in content.find(True,attrs={ 'class': 'levelWrap' }).find_all('p'):
        leveltext  += line.text + '\n'
    array.append(leveltext)
    detailtexts = content.find_all(True,attrs={ 'class': 'txt cardtext' })
    text = ""
    for detailtext in detailtexts:
        for i in detailtext.select("br"):
            i.replace_with('\n')
        text += detailtext.text.replace(' ', '').replace('\r', '')+'\n'
    array.append(text)
    #print ("createarray END")
    
def stragecash(contents,cashlist,both):
    cardnum = searchcardlist(contents[0],cashlist)
    if cardnum ==-1:
        cardnum = len(cashlist)
        card = [contents[0]]
        if both:
            carddetail = contenthtml("https://club.battlespirits.com/bsclub/mydeck/detail2/?id="+contents[0]+"&info28="+contents[1]+"&nomydeck_flg="+contents[2]+"&available="+contents[3])
            sidea = carddetail.find(id="side-a")
            sideb = carddetail.find(id="side-b")
            createarray(sidea,sidea.find(True,attrs={ 'class': 'num' }).text,card)
            card.append(True)
            createarray(sideb,sideb.find(True,attrs={ 'class': 'num' }).text+"_b",card)
        else:
            carddetail = contenthtml("https://club.battlespirits.com/bsclub/mydeck/detail/?id="+contents[0]+"&info28="+contents[1]+"&nomydeck_flg="+contents[2]+"&available="+contents[3])
            createarray(carddetail.find(True, attrs={ 'class': 'detail' }),carddetail.find(True,attrs={ 'class': 'num' }).text,card)
            card.append(False)
        cashlist.append(card)
    return cashlist[cardnum][0]
    #print ("stragecash END")

def batospibu(deck,cashedcardlist,deckurl):
    deck = []
    inner = contenthtml(deckurl).find(True, attrs={ 'class': 'inner' })    # classが「inner」を検索
    deck.append(inner.find('h2').text)
    cardlistBox = inner.find(True, attrs={ 'class': 'cardlistBox' })    # classが「cardlistBox」を検索
    for card in cardlistBox.find_all("li"):    # その中のliタグの文字列を表示
        targeturl = card.find(True, attrs={ 'class': 'detail' })    # classが「detail」を検索
        hrefcontent = targeturl.get('href','javasrcipt:cardDetails(\'0\' ,\'0\',\'\',\'0\')').replace('\'', '').replace('\s', '')
        if('javascript:cardDetails2' in hrefcontent):
            cardcontents = hrefcontent[24:-1].split(',')
            cardnum = [stragecash(cardcontents,cashedcardlist,True)]
        else:
            cardcontents = hrefcontent[23:-1].split(',')
            cardnum = [stragecash(cardcontents,cashedcardlist,False)]
        cardnum.append(card.find(True,attrs={ 'class': 'cardCount' }).text)
        deck.append(cardnum)
    return deck
    #print ("batosupibu END")

def deckcreate():
#デッキリスト取得
    global decklist,cashedcardlist
    try:
        with open(find_data_file('./cardcash/deck.pkl'),mode='rb') as f:
            decklist = pickle.load(f)
    except OSError as e:
        print(e)
        decklist = []
#decklist=[[deckname,[card,num],...],...]

#キャッシュ済みカードリスト取得
    try:
        with open(find_data_file('./cardcash/cash.pkl'),mode='rb') as f:
            cashedcardlist = pickle.load(f)
    except OSError as e:
        print(e)
        cashedcardlist = []

#cashedcardlist=[[id:,number:,name:,category:,color:,cost:,reduction:,attribute:,levelWarp:([[3000,1],[6000,3],[0,0],...]),cardtext:,both:,(裏面側number:,...)],...]

#デッキ選択、取得
    if not decklist == []:
        print ("使うデッキを選択してください")
        print ("0:バトスピ部から取得")
        i = 1
        max = len(decklist)
        for dispdeck in decklist:
            print ("{}:{}".format(i,dispdeck[0]))
            i+=1
        try:
            while (True):
                select = int(input (">>"))
                if select<0 or max<select:
                    print ("0~{}を入力してください".format(max))
                else:
                    break
        except ValueError:
            select = 0
    else:
        select = 0
    if not (select == 0):
        deck = decklist[select-1]
#バトスピ部のデッキ解析
    else:
        print ("バトスピ部のデッキurlを入力してください")
        deckurl = input (">>")
        deck = batospibu([],cashedcardlist,deckurl)
        decklist.append(deck)
#キャッシュ保存
        with open(find_data_file('./cardcash/cash.pkl'),'wb') as file:
            pickle.dump(cashedcardlist, file)
#デッキ保存
        with open(find_data_file('./cardcash/deck.pkl'),'wb') as file:
            pickle.dump(decklist, file)
    #print ("deckcreate END")
    deckcopy = copy.copy(deck)
    deckcopy.pop(0)
    return deckcopy

def sampleImageCreate():
    # 画像のファイル保存
    img = Image.new("L", (CARD_WIDTH, CARD_HEIGHT), 255)
    # 画像のファイル保存
    img.save(find_data_file("./cardcash/sample.png"))



#コントローラークラス
class Contraller(tk.Frame):
    def __init__(self,master=None):
        self.decksource = deckcreate()
        
        super().__init__(master)
        self.master.geometry("1260x918")
        self.master.title("batspi_simulator v0.0.1")
        self.pack()
#環境作成
        self.width = CARD_WIDTH*12
        self.height = CARD_HEIGHT*6
        self.images = []
        self.deck = []
        self.hand = []
        self.open = []
        self.trash = []
        self.field =[]
        self.engagesprit = False
        self.detailimg = []
        self.message = []
        self.core=[]
        self.card_fig_id = 0
        self.card_core_id = 0

        self.createWidgets()  # キャンバス作成
        self.createCards()  # カードを作成
        self.layoutSet() # ボタンを並べる+初期化

#関数群

#キャンバス作成系列
    def createWidgets(self):
        '''アプリに必要なウィジェットを作成する'''
        
        #print ("createWidgets start")
        self.canvas = tk.Canvas(
            self.master,
            width=self.width,
            height=self.height,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack()
        #print ("createWidgets END")


#ボタンを並べる+初期化系列
    def layoutSet(self):
        #デッキ画像を用意
        self.canvas.create_rectangle(CARD_WIDTH*11, 0, CARD_WIDTH*12, CARD_HEIGHT,fill="blue")
        #コアを用意
        self.coreSet()
        #詳細欄表示
        sampleImageCreate()
        self.canvas.create_rectangle(0, 0, CARD_WIDTH*2, CARD_HEIGHT*6-BUTTON_HEIGHT*2,fill="#aaaaaa")
        self.detailimg = tk.PhotoImage(file=find_data_file("./cardcash/sample.png"), width=CARD_WIDTH, height=CARD_HEIGHT)
        self.canvas.create_image(CARD_WIDTH/2, 0,image = self.detailimg, anchor = tk.NW)
        self.message =  self.canvas.create_text(CARD_WIDTH, CARD_HEIGHT+(CARD_HEIGHT*5-BUTTON_HEIGHT)/2,text="",width = 200,tag = "text")
        #ボタンを用意
        self.buttonSet()
        #print ("layoutset END")

    def coreSet(self):
        #コアを用意
        for i in range(4):
            for j in range(8):
                self.core.append(self.canvas.create_oval(CARD_WIDTH*2+i*20,CARD_HEIGHT+10+j*20,CARD_WIDTH*2+i*20+20,CARD_HEIGHT+10+j*20+20,fill="blue",tag="core"))
        self.core.append(self.canvas.create_oval(CARD_WIDTH*2,CARD_HEIGHT-10,CARD_WIDTH*2+20,CARD_HEIGHT+10,fill="red",tag="core"))
        self.canvas.tag_bind("core","<ButtonPress-1>", self.clickCore)
        self.canvas.tag_bind("core","<B1-Motion>", self.dragCore)
        #print ("coreset END")

    def buttonSet(self):
        #ボタンを用意
        self.buttontop = self.canvas.create_rectangle(CARD_WIDTH*11,CARD_HEIGHT,CARD_WIDTH*11+BUTTON_WIDTH,CARD_HEIGHT+BUTTON_HEIGHT,fill="#aaaaaa",tag="buttontop")
        self.canvas.create_text(CARD_WIDTH*11+BUTTON_WIDTH/2, CARD_HEIGHT+BUTTON_HEIGHT/2, text = "上からドロー",tag="buttontop")
        self.canvas.tag_bind("buttontop","<ButtonPress-1>", self.get_card_top)
        self.buttonbottom = self.canvas.create_rectangle(CARD_WIDTH*11,CARD_HEIGHT+BUTTON_HEIGHT,CARD_WIDTH*11+BUTTON_WIDTH,CARD_HEIGHT+BUTTON_HEIGHT*2,fill="#aaaaaa",tag="buttonbottom")
        self.canvas.create_text(CARD_WIDTH*11+BUTTON_WIDTH/2, CARD_HEIGHT+BUTTON_HEIGHT*3/2, text = "下からドロー",tag="buttonbottom")
        self.canvas.tag_bind("buttonbottom","<ButtonPress-1>", self.get_card_bottom)
        self.buttonbacktop = self.canvas.create_rectangle(0,CARD_HEIGHT*6-BUTTON_HEIGHT,BUTTON_WIDTH,CARD_HEIGHT*6,fill="#aaaaaa",tag="buttonbacktop")
        self.canvas.create_text(BUTTON_WIDTH/2,CARD_HEIGHT*6-BUTTON_HEIGHT/2, text = "上に戻す",tag="buttonbacktop")
        self.canvas.tag_bind("buttonbacktop","<ButtonPress-1>", self.back_card_top)
        self.buttonbackbottom = self.canvas.create_rectangle(BUTTON_WIDTH,CARD_HEIGHT*6-BUTTON_HEIGHT,BUTTON_WIDTH*2,CARD_HEIGHT*6,fill="#aaaaaa",tag="buttonbackbottom")
        self.canvas.create_text(BUTTON_WIDTH*3/2,CARD_HEIGHT*6-BUTTON_HEIGHT/2, text = "下に戻す",tag="buttonbackbottom")
        self.canvas.tag_bind("buttonbackbottom","<ButtonPress-1>", self.back_card_bottom)
        self.buttonres = self.canvas.create_rectangle(0,CARD_HEIGHT*6-BUTTON_HEIGHT*2,BUTTON_WIDTH,CARD_HEIGHT*6-BUTTON_HEIGHT,fill="#aaaaaa",tag="buttonreset")
        self.canvas.create_text(BUTTON_WIDTH/2,CARD_HEIGHT*6-BUTTON_HEIGHT*3/2,text = "リセット",tag="buttonreset")
        self.canvas.tag_bind("buttonreset","<ButtonPress-1>", self.reset)
        self.buttonrev = self.canvas.create_rectangle(BUTTON_WIDTH,CARD_HEIGHT*6-BUTTON_HEIGHT*2,BUTTON_WIDTH*2,CARD_HEIGHT*6-BUTTON_HEIGHT,fill="#aaaaaa",tag="buttonreverse")
        self.canvas.create_text(BUTTON_WIDTH*3/2,CARD_HEIGHT*6-BUTTON_HEIGHT*3/2,text = "裏返す",tag="buttonreverse")
        self.canvas.tag_bind("buttonreverse","<ButtonPress-1>", self.reverseCard)
        #print ("buttonSet END")

    def detailReset(self):
        #詳細欄の初期化
        sampleImageCreate()
        self.detailimg.config(file=find_data_file("./cardcash/sample.png"))
        detailtext=""
        self.canvas.itemconfig(self.message,text=detailtext)
        self.card_fig_id = 0
        self.card_core_id = 0
        #print ("detailReset END")
   

# カードを作成系列
    def createCards(self):
        for card in self.decksource:
            if not type(card) == 'int':
                for index in range(int(re.search(r'\d+', card[1]).group())):
                    self.deck.append(card[0])
                    carddetail = cashedcardlist[searchcardlist(card[0],cashedcardlist)]
                    if not self.engagesprit and  carddetail[3] =="契約スピリット":
                        self.get_card_bottom() 
                        self.engagesprit = True
        self.cardDist()
        #print ("createCards END")

    def cardDist(self):
        self.shuffle()
        for num in range(3):
            self.get_card_top() 
        if not self.engagesprit:
            self.get_card_top ()
        #print ("cardDist END")

    def layoutCards(self,contents):
        '''カードをキャンバス上に並べる'''

        content = cashedcardlist[searchcardlist(contents,cashedcardlist)]
        self.appearCards(content)
        return content

    def appearCards(self,content):
        '''カードをキャンバス上に並べる'''
        # 画像を描画
        fig = tk.PhotoImage(file=find_data_file("./cardcash/"+content[1]+".png"))
        self.images.append(fig)
        figid = self.canvas.create_image(CARD_WIDTH*3+random.randrange(-10,10,1), CARD_HEIGHT*4+random.randrange(-10,10,1),tag="card",image = fig)

        # フィールドにあるカードとしてリストに追加
        self.field.append([figid,content])
        self.canvas.tag_bind("card","<ButtonPress-1>", self.selectCard)
        self.canvas.tag_bind("card","<B1-Motion>", self.dragCard)

        #tagをnumberに変更
        #print ("layoutCards END")
        return

#イベント系統の関数
    def selectCard(self, event):
        '''選択されたカードに対する処理'''

        x = event.x
        y = event.y
        # クリックされたカードに対応する図形IDを取得
        card_fig_ids = self.canvas.find_closest(x,y)
        self.card_fig_id = card_fig_ids[0]
        for check in self.field:
            if(check[0] == self.card_fig_id):
        #詳細欄の更新
                self.detailimg.config(file=find_data_file("./cardcash/"+check[1][1]+".png"))
                detailtext=""
                for i in range(9):
                    if i == 5:
                        for coler in check[1][6]:
                            detailtext += coler
                        detailtext += "\n"
                    else:
                        detailtext+=check[1][i+1]+"\n"
                self.canvas.itemconfig(self.message,text=detailtext)
                break
        # マウスの座標を記憶
        self.before_x = x
        self.before_y = y
        #print ("select END")

    def dragCard(self,event):
        x = event.x
        y = event.y

        # 前回からのマウスの移動量の分だけ図形も移動
        self.canvas.move(
            self.card_fig_id,
            x - self.before_x, y - self.before_y
        )

        # マウスの座標を記憶
        self.before_x = x
        self.before_y = y

    def clickCore(self,event):
        x = event.x
        y = event.y
        # クリックされたカードに対応する図形IDを取得
        card_core_ids = self.canvas.find_closest(event.x, event.y)
        self.card_core_id = card_core_ids[0]
        #コアのレイヤーをトップに
        for corelayer in self.core:
            self.canvas.tag_raise(corelayer)
        # マウスの座標を記憶
        self.before_x = x
        self.before_y = y
        #print ("select END")

    def dragCore(self,event):
        x = event.x
        y = event.y
        # 前回からのマウスの移動量の分だけ図形も移動
        self.canvas.move(
            self.card_core_id,
            x - self.before_x, y - self.before_y
        )
        # マウスの座標を記憶
        self.before_x = x
        self.before_y = y

    def get_card_top(self,event = 0):
        #上から引く
        if len(self.deck) == 0:
            return
        self.hand.append(self.layoutCards(self.deck.pop(0)))
        #print ("getcardtop END")
        
    def get_card_bottom(self,event = 0):
        #下から引く
        if len(self.deck) == 0:
            return
        self.hand.append(self.layoutCards(self.deck.pop(-1)))
        #print ("getcardbottom END")

    def back_card_top(self,event = 0):
        #上に戻す
        if len(self.field) == 0:
            return
        for check in self.field:
            if(check[0] == self.card_fig_id):
                self.deck.insert(0,check[1][0])
                self.field.remove(check)
                self.canvas.delete(check[0])
                self.detailReset()
                break
        #print ("backcardtop END")
        
    def back_card_bottom(self,event = 0):
        #下に戻す
        if len(self.field) == 0:
            return
        for check in self.field:
            if(check[0] == self.card_fig_id):
                self.deck.append(check[1][0])
                self.field.remove(check)
                self.canvas.delete(check[0])
                self.detailReset()
                break
        #print ("backcardbottom END")

    def reverseCard(self,event = 0):
        #転醒(裏返し)処理
        for check in self.field:
            if(check[0] == self.card_fig_id):
                if check[1][10]:
                    for i in range(9):
                        check[1].insert(i+1,check[1][2*i+11])
                    check[1].insert(10,True)
                    del check[1][20:]
                    fig = tk.PhotoImage(file=find_data_file("./cardcash/"+check[1][1]+".png"))
                    self.images.append(fig)
                    self.canvas.itemconfigure(check[0],image = fig)
                break

    def shuffle(self):
        #シャッフル
        random.shuffle(self.deck)
        #print ("shuffle END")

    def reset(self,event = 0):
        #振り分け直し
        self.engagesprit = False
        self.canvas.delete("card")
        self.deck.clear()
        self.field.clear()
        self.hand.clear()
        self.canvas.delete("core")
        self.detailReset()
        self.coreSet()
        self.createCards()
        #print ("reset END")


#以降未使用関数
    def open_card_top(self,event = 0):
        if len(self.deck) == 0:
            return
        for index in range(card_num):
            self.hand.append(self.deck[index])
        
    def open_card_bottom(self,event = 0):
        if len(self.deck) == 0:
            return
        for index in range(card_num):
            self.card_list.append(self.deck[len(self.deck)-1-index])
        

#メイン関数
def main():
    ctrl = tk.Tk()
    app = Contraller(master = ctrl)
    app.mainloop()

#メイン
if __name__ == '__main__':
    main()






#カードデータスクレイピング用url
#https://club.battlespirits.com/bsclub/mydeck/detail/?id=150937&info28=BS51

#デッキデータスクレイピング用url
#https://club.battlespirits.com/bsclub/mydeck/decksrc/202306/11686894944337_20230616.html
#https://club.battlespirits.com/bsclub/mydeck/decksrc/202306/11687096911622_20230618.html
