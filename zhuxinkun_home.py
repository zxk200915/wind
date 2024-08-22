import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_drawable_canvas import st_canvas
from audio_recorder_streamlit import audio_recorder
import pandas as pd
import time
from PIL import Image, ImageOps, ImageFilter
import requests
import os
import json
import uuid
import hashlib
import io
import base64  
import urllib.parse


page = st.sidebar.radio("首页",["游戏推荐","动作类游戏","冒险类游戏","射击游戏","角色扮演游戏","游戏搜索","图片处理","留言区"])

def getvoice(text):
    url = 'https://openapi.youdao.com/api'
    data = {
        'q': text,
        'from': 'auto',
        'to': 'en',
        'ext': 'mp3',
        'appKey': '74d2408d4034972b',
        'salt': str(uuid.uuid1()), 
        'signType': 'v3',
        'curtime': str(int(time.time()))
    }
    sha = hashlib.sha256()
    q = data['q'] if len(data['q']) <= 20 else data['q'][:10] + len(data['q']) + data['q'][-10:]
    sha.update((data['appKey'] + q + data['salt'] + data['curtime'] + 'mbccomD3aoyJm20n0aWTU3ZrtvrKl8xC').encode('utf-8'))
    data['sign'] = sha.hexdigest()
    sent_content = requests.post(url, data=data)
    res_content = sent_content.json()
    return res_content['tSpeakUrl']

def get_yiyan():
    url = f"https://v1.hitokoto.cn/?encode=json"
    response = requests.get(url)
    data = response.json()  
    # 解析返回的 JSON 数据,提取 "hitokoto" 字段的值  
    result = data["hitokoto"]
    return result

def get_weather(city_name):
    if city_name:
        url = "https://api.gumengya.com/Api/Weather?format=json&scene=1&city={}".format(city_name)
        response = requests.get(url)
        data = response.json()
        # 提取now对象的text和temperature字段的值  
        text = data['data']['now']['text']  
        temperature = data['data']['now']['temperature']
        temperature = temperature + "℃"
        markdown = '''
        **{}**
        **{}**
        ![](https://imsuk.cn/streamlit/{}.png)
        '''
        markdown = markdown.format(text,temperature,text)
    else:
        markdown = '''**请输入城市名称**'''
    return markdown
  
def get_hot():
    # 获取数据  
    url = 'https://api.gumengya.com/Api/BaiduTieBaHot?format=json'  # 替换为你的数据源URL  
    response = requests.get(url)  
    data = response.json()  
    data = data['data']
    # 处理数据 
    ps = pd.DataFrame(data) 
    ps = ps.head(10)
    return ps

API_KEY = "RjOLGPrDhOk6OFsz9ZWP1FTj"
SECRET_KEY = "BvyqbKHucjQmjD16o5mbQaBBQLDvIfXG"

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def get_ocr(image):
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token=" + get_access_token()
    payload='image={}'.format(image)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    words_result = data["words_result"]  
    words_list = [word["words"] for word in words_result] 
    return words_list

def base64_img(img):
    encoded_image = base64.b64encode(img)  
    # 将base64编码的字符串进行URL编码  
    encoded_image_url = urllib.parse.quote(encoded_image.decode('utf-8'))
    return encoded_image_url

def check_file_content(file_path):  
    # 检查文件是否存在且不为空  
    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:  
        return True  
    return False

    
def img_change(img,rc,gc,bc):
    '''图片处理'''
    width,height=img.size
    img_array = img.load()
    for x in range(width):
        for y in range(height):
            r = img_array[x,y][rc]
            g = img_array[x,y][gc]
            b = img_array[x,y][bc]
            img_array[x,y]=(r,g,b)
    return img
def img_change_ch(img):
    '''图片反色滤镜'''
    width, height = img.size
    img_array = img.load()
    for x in range(width):
        for y in range(height):
            # 获取RGB值，反色处理
            r = 255 - img_array[x, y][0]
            g = 255 - img_array[x, y][1]
            b = 255 - img_array[x, y][2]
            img_array[x, y] = (r, g, b)
    return img
def img_change_co(img):
    '''增强对比度滤镜'''
    width, height = img.size
    img_array = img.load()
    for x in range(width):
        for y in range(height):
            # 获取RGB值
            r = img_array[x, y][0]
            g = img_array[x, y][1]
            b = img_array[x, y][2]
            # RGB值中，哪个更大，就再大一些
            if r == max(r, g, b):
                if r >= 200:
                    r = 255
                else:
                    r += 55
            elif g == max(r, g, b):
                if g >= 200:
                    g = 255
                else:
                    g += 55
            else:
                if b >= 200:
                    b = 255
                else:
                    b += 55
            img_array[x, y] = (r, g, b)
    return img

def img_change_bw(img):
    '''图片黑白滤镜'''
    img = img.convert('L') # 转换为灰度图
    return img 

def page1():
    """游戏推荐"""
    st.title("青玄网")
    st.snow()
    st.image("s.png")
    st.write('音乐推荐')    
    imgs_name_lst = ['2.png', '4.png']
    imgs_lst = []
    for i in imgs_name_lst:
        img = Image.open(i)
        img = img.resize((1000, 1000))
        imgs_lst.append(img)
    col1, col2 = st.columns([1,1])
    with col1:
        st.image(imgs_lst[0])
        st.write("Teeth")
        with open('Teeth.mp3',"rb")as f:
            music =f.read()
            st.audio(music,format='audio/mp3',start_time=8)
    with col2:
        st.image(imgs_lst[1])
        st.write("Wake")
        with open('Wake.mp3',"rb")as f:
            music =f.read()
            st.audio(music,format='audio/mp3',start_time=8)

    imgs_name_lst = ['3.png', '5.png']
    imgs_lst = []
    for i in imgs_name_lst:
        img = Image.open(i)
        img = img.resize((1000, 1000))
        imgs_lst.append(img)
    let1, let2 = st.columns([1,1])
            
    with let1:
        st.image(imgs_lst[0])
        st.write("Tamada")
        with open('Tamada.mp3',"rb")as f:
            music =f.read()
            st.audio(music,format='audio/mp3',start_time=8)
    with let2:
        st.image(imgs_lst[1])
        st.write("天下")
        with open('tx.mp3',"rb")as f:
            music =f.read()
            st.audio(music,format='audio/mp3',start_time=8)

    st.write(" ")
    st.write('游戏推荐')  
    tab1,tab2,tab3,tab4 =st.tabs(["王者荣耀","猫和老鼠","我的世界","和平精英"])
    with tab1:
        st.write("王者荣耀中的玩法以竞技对战为主，玩家之间进行1V1、3V3、5V5等多种方式的PVP对战，在满足条件后可以参加游戏的排位赛等，还可以参加PVE的闯关模式，是属于推塔类型的游戏。")
        st.image("c.jpg")
        st.image("d.png")
    with tab2:
        st.write("游戏采用实时联网多人对战模式，有9种玩法：经典模式、5v5、跑酷、天梯模式、玩吧、谁是外星人、战队赛、多元乱斗和自定义模式。经典模式每局游戏由5名玩家组成，1名玩家扮演猫，4名玩家扮演老鼠。")
        st.image("h.png")
        st.image("g.png")
    with tab3:
        st.write("该游戏以玩家在一个充满着方块的三维空间中自由地创造和破坏不同种类的方块为主题。玩家在游戏中可以在单人或多人模式中通过摧毁或创造精妙绝伦的建筑物和艺术，或者收集物品探索地图以完成游戏的成就（进度）。玩家也可以尝试在创造模式下(打开作弊)红石电路和指令等玩法。")
        st.image("e.png")
        st.image("f.png")
    with tab4:
        st.write("该游戏采用虚幻4引擎研发，沿袭端游《绝地求生》的玩法，以及前作《绝地求生：刺激战场》与《绝地求生：全军出击》的运营模式，致力于从画面、地图、射击手感等多个层面还原原始端游数据，为玩家全方位打造出极具真实感的军事竞赛体验。")
        st.image("a.png")
        st.image("b.png")
    

    
def page2():
    """动作类游戏"""
    st.title("动作类游戏")
    st.header("动作游戏的定义")
    st.write("动作游戏（Action Game）是一种广义上以“动作”作为游戏主要表现形式的游戏即可算作动作游戏的游戏类型。游戏基本剧情较为简单，主要是通过熟悉操作技巧就可以进行游戏且一般比较都有刺激性，情节紧张，但比较操作简单。动作游戏包含射击和格斗游戏。")
    st.write(" ")
   
    choice = st.radio(
        '你玩过动作类的游戏？',
        ['一直玩', '常常玩', '很少玩',"没玩过"],
        captions=['这是第一个选项', '这是第二个选项', '这是第三个选项','这是第四个选项']
    )
    st.write(" ")
    st.write("动作游戏推荐")    
    imgs_name_lst = ['k.png', 'l.png']
    imgs_lst = []
    for i in imgs_name_lst:
        img = Image.open(i)
        img = img.resize((1200, 800))
        imgs_lst.append(img)
    col1, col2 = st.columns([1,1])
    with col1:
        st.image(imgs_lst[0])
        st.link_button('使命召唤基础攻略', 'https://www.bilibili.com/video/BV1Dy421a7y9/?spm_id_from=333.337.search-card.all.click')
        st.write("《使命召唤手游》（Call of Duty Mobile简称：CODM）是由深圳市腾讯计算机系统有限公司制作发行的一款大型多人在线第一人称射击类游戏，该作于2020年12月25日正式公开测试,游戏有冲锋团队竞技、经典爆破、个人竞技、热点站、战术团队竞技、据点争夺、抢牌行动、夺命双雄八大常驻模式及亡者之袭、躲猫猫、狼人迷踪等休闲模式，还有地面战争、打雪仗等限时模式，以及100人大地图的使命战场模式和多种PVE挑战模式。")
            
    with col2:
        st.image(imgs_lst[1])
        st.link_button('元气骑士基础攻略', 'https://www.bilibili.com/video/BV143411H74r/?spm_id_from=333.337.search-card.all.click')
        st.write("元气骑士是一款动作类游戏，玩家扮演一个被黑客控制的骑士，在游戏中完成各种任务，击败敌人。游戏具有高复玩性以及独特的动作设计，玩家可以通过打击敌人来获得分数，并且游戏具有自由度较高的特点。玩家可以通过升级来解锁新的技能和装备，提升战斗能力。同时，游戏也提供了丰富的故事情节，玩家可以与游戏中的敌人进行战斗，体验不同的游戏体验。")


def page3():
    """冒险类游戏"""
    pass
def page4():
    """射击游戏"""
    pass
def page5():
    """角色扮演游戏"""
    pass
def page6():
    """游戏搜索"""
    st.write('游戏搜索')
    with open('游戏.txt','r',encoding='utf-8')as f:
        game_list =f.read().split('\n')
    for i in range(len(game_list)):
        game_list[i]=game_list[i].split('#')
    game_dict = {}
    for i in game_list:
        game_dict[i[1]]=[int(i[0]),i[2]]
    with open('check_out_times.txt','r',encoding='utf-8')as f:
        times_list =f.read().split('\n')#将列表转为字典
    for i in range(len(times_list)):
        times_list[i]=times_list[i].split('#')
    times_dict ={}
    for i in times_list:
        times_dict[int(i[0])]=int(i[1])
    word =st.text_input('请输入要查询的游戏')
    if word in game_dict:
        st.write(game_dict[word])
        if word =='猫和老鼠':
            st.balloons()
        n =game_dict[word][0]
        if n in times_dict:
            times_dict[n]+=1
        else:
            times_dict[n]=1
            
        with open('check_out_times.txt','w',encoding='utf-8')as f:
            message = ''
            for k,v in times_dict.items():
                message +=str(k)+'#'+str(v)+'\n'
            message =message[:-1]
            f.write(message)
        st.write('查询次数：',times_dict[n])


def page7():
    '''图片处理'''
    st.header(':sun_with_face:图片处理工具:sun_with_face:')
    uploaded_file = st.file_uploader('上传图片',type=['png','jpg','jpeg'])
    my_bar = st.progress(0)
    #name = uploaded_file.name
    #size = uploaded_file.size
    #type = uploaded_file.type
    #st.write(name,size,type)
    if uploaded_file:
        # 获取图片文件的名称、类型和大小
        file_name = uploaded_file.name
        file_type = uploaded_file.type
        file_size = uploaded_file.size
        img = Image.open(uploaded_file)
        # 显示图片处理界面
        col1, col2, col3 = st.columns([3, 2, 4])
        with col1:
            st.image(img)
        with col2:
            ch = st.toggle('反色滤镜')
            co = st.toggle('增强对比度')
            bw = st.toggle('黑白滤镜')
        with col3:
            st.write('对图片进行反色处理')
            st.write('让图片颜色更加鲜艳')
            st.write('将图片变为灰度图')
        # 点击按钮处理图片
        b = st.button('开始处理')
        l = [ch,co,bw]
        if b:
            if l:
                roading = st.progress(0, '开始加载')
                for i in range(1, 101, 1):
                    time.sleep(0.02)
                    roading.progress(i, '正在加载'+str(i)+'%')
                roading.progress(100, '加载完毕！')
                img = img_change_ch(img)
            # if co:
            #     roading = st.progress(0, '开始加载')
            #     for i in range(1, 101, 1):
            #     img = img_change_co(img)
            # if bw:
            #     roading = st.progress(0, '开始加载')
            #     for i in range(1, 101, 1):
            #     img = img_change_bw(img)
            st.write('右键"另存为"保存图片')
            st.image(img)


def process_message():
    play_list=[]

def page8():
    """留言区"""
    st.header("留言框",anchor=False,divider="rainbow")
    play_list=[]
    
    #读取文件
    try:#判断是否有留言文本文件
        with open("messages.txt",'r',encoding="utf-8")as mes:
            play_list=mes.read().split("\n")#读取留言文本字典
            if play_list[-1]=="":
                play_list.pop()#删除最后的空项
            for i in range(len(play_list)):
                play_list[i]=play_list[i].split("#")#以:具体分割每个留言的详细信息
                
    except FileNotFoundError:#如果没有留言文件
        with open("messages.txt",'w',encoding="utf-8")as mes:#创建文件
            mes.write("")

    #显示文本([1]:名字,[2]:头像,[3]:信息内容,[4]:时间)
    mes_con=st.container(border=True)#创建容器框
    no_message=False#是否无留言
    with mes_con:
        for message in play_list:#遍历消息列表
            # st.write(f"**{message[1]}**&nbsp;&nbsp;(:gray[{message[4]}]):")#书写用户名
            with st.chat_message(name=message[1],avatar=message[2]):#创建消息框
                st.write(f"""######  **{message[1]}**&nbsp;&nbsp;(:gray[{message[4]}]):  
                         {message[3]}""")#书写留言信息
        #清空留言区按钮     
        if play_list:
            message_space,message_col=st.columns([0.75,0.25])#并列容器
            with message_col:
                if st.button("清空留言区",type="primary",use_container_width=True):
                    os.remove("messages.txt")    
                    st.rerun()
        else:
            no_message=True
        if no_message:        
            st.caption("暂无人发布消息哦~快去抢沙发吧!")


        
        

    #留言交互
    mes_input_con=st.container(border=True)#创建容器框
    with mes_input_con:
        # with st.empty():
        st.write("**留言区:**")
        user_name_text,user_name_col,user_avatar_text,user_avatar_col=st.columns([0.1,0.5,0.09,0.31])
        with user_name_text:
            st.write("用户名:")
        with user_name_col:
            user_name=st.text_input(" ",placeholder="输入你的用户名...",label_visibility="collapsed")
        with user_avatar_text:
            st.write("头像:")
        with user_avatar_col:
            user_avatar=st.selectbox(" ",["🧑","🧒","🧓","🧔","🧐","🌖","🌞","🌛","🌤️","🌺","🍋","🍄","🎃","🎅","🎸","☃️","🧛‍♀️","😃","😍","😜","📺","😨","😔"],index=None,placeholder="选择一个头像吧...",label_visibility="collapsed")
        input_message_col,enter_message_col=st.columns([0.9,0.1])#并列容器
        with input_message_col:
            input_message=st.text_input(" ",placeholder="输入你想说的话吧...",label_visibility="collapsed")

        #输入保存
        with enter_message_col:
            enter_message=st.button("留言",type="primary",use_container_width=True)
        if enter_message:
            if user_name and user_avatar and input_message:
                now_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())#获取当前时间
                if play_list:#判断消息列表是否有消息
                    play_list.append([str(int(play_list[-1][0])+1),user_name,user_avatar,input_message,now_time])#将用户名,头像,输入的文本添加到消息列表的最后
                else:
                    play_list.append([str(1),user_name,user_avatar,input_message,now_time])#将用户名,头像,输入的文本添加到消息列表的最后,序号因为没有消息所以直接为1
                with open("messages.txt",'w',encoding="utf-8")as mes:#打开文件准备写入
                    writein_str=""#预写入的字符串
                    for message in play_list:#遍历消息列表
                        writein_str+=("#").join(message)+"\n"#组合文本格式添加到预写入的字符串
                    writein_str=writein_str[:-1]#清除结尾换行
                    mes.write(writein_str)#写入文本
                with open("messages.txt",'r',encoding="utf-8")as mes:
                    st.rerun()
            else:
                st.warning('👆👆&nbsp;&nbsp;&nbsp;&nbsp;好像有信息没有填充完整哦😕')

if page == "游戏推荐":
    page1()
elif page=="动作类游戏":
    page2()
elif page=="冒险类游戏":
    page3()
elif page=="射击游戏":
    page4()
elif page=="角色扮演游戏":
    page5()
elif page=="游戏搜索":
    page6()
elif page=="图片处理":
    page7()
elif page=="留言区":
    page8()


with st.sidebar:
    with st.spinner('加载中,no着急...'):
        time.sleep(0.8)
with st.sidebar:
    col1, col2 = st.columns([2,1])
    with col1:
        city = st.text_input('输入你要查询天气的城市名称','上海市')
    with col2:
        st.markdown(get_weather(city))
    # 设置热搜榜的样式和布局  
    hot = get_hot()
    st.title('热搜榜')
    for i, row in hot.iterrows():
        row.rename({'title': '标题', 'hot': '热度', 'description': '详细'}, inplace=True)
        row = row.drop('updatetime', axis=0)
        st.write(row.drop('url', axis=0))  # 直接返回整个数据行
        if i < len(hot) - 1:  # 如果不是最后一条，添加分隔线
            st.link_button("点此打开热搜", row['url'])
            st.write('-' * 8)