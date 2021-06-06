import time
import random
import requests
from selenium import webdriver
from urllib.request import urlretrieve
from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

class Ffxivclass():
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')  #windows可以去掉
        chrome_options.add_argument('--disable-gpu') #windows可以去掉
        chrome_options.add_argument('window-size=1920x3000') #windows可以去掉
        chrome_options.add_argument('--disable-dev-shm-usage') #windows可以去掉
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
        self.driver = webdriver.Chrome(executable_path='/files/python_code/ffxiv_sign/chromedriver',options=chrome_options)#指定驱动目录
        
    def get_img(self,src):
        src_bg = src.replace('index=1', 'index=0')
        src_bg = src_bg.replace('img_index=1', 'img_index=0')
        # print(src_bg)
        # 将图片下载到本地
        urlretrieve(src, 'img1.png')
        urlretrieve(src_bg, 'img2.png')
        # 读取本地图片
        captcha1 = Image.open('img1.png')
        captcha2 = Image.open('img2.png')
        return captcha1, captcha2


    def resize_img(self,img):
        """
        下载的图片把网页中的图片进行了放大，所以将图片还原成原尺寸
        :param img: 图片
        :return: 返回还原后的图片
        """
        # 通过本地图片与原网页图片的比较，计算出的缩放比例 原图（680x390）缩小图（280x161）
        a = 2.428
        (x, y) = img.size
        x_resize = int(x // a)
        y_resize = int(y // a)
        """
        Image.NEAREST ：低质量
        Image.BILINEAR：双线性
        Image.BICUBIC ：三次样条插值
        Image.ANTIALIAS：高质量
        """
        img = img.resize((x_resize, y_resize), Image.ANTIALIAS)
        return img


    def is_pixel_equal(self,img1, img2, x, y):
        """
        比较两张图片同一点上的像数值，差距大于设置标准返回False
        :param img1: 阴影图
        :param img2: 原图
        :param x: 横坐标
        :param y: 纵坐标
        :return: 是否相等
        """
        pixel1, pixel2 = img1.load()[x, y], img2.load()[x, y]
        sub_index = 100
        # 比较RGB各分量的值
        if abs(pixel1[0] - pixel2[0]) < sub_index and abs(pixel1[1] - pixel2[1]) < sub_index and abs(
                pixel1[2] - pixel2[2]) < sub_index:
            return True
        else:
            return False


    def get_gap_offset(self,img1, img2):
        """
        获取缺口的偏移量
        """
        distance = 70
        for i in range(distance, img1.size[0]):
            for j in range(img1.size[1]):
                # 两张图片对比,(i,j)像素点的RGB差距，过大则该x为偏移值
                if not self.is_pixel_equal(img1, img2, i, j):
                    distance = i
                    return distance
        return distance


    def get_track(self,distance):
        """
        计算滑块的移动轨迹
        """
        # 通过观察发现滑块并不是从0开始移动，有一个初始值
        distance -= 30
        a = distance / 4
        track = [a, a, a, a]
        return track


    def shake_mouse(self):
        """
        模拟人手释放鼠标抖动
        """
        ActionChains(self.driver).move_by_offset(xoffset=-2, yoffset=0).perform()
        ActionChains(self.driver).move_by_offset(xoffset=2, yoffset=0).perform()


    def operate_slider(self,track):
        """
        拖动滑块
        当你调用ActionChains的方法时，不会立即执行，而是会将所有的操作按顺序存放在一个队列里，当你调用perform()方法时，队列中的时间会依次执行。
        :param track: 运动轨迹
        :return:
        """
        # 定位到拖动按钮
        slider_bt = self.driver.find_element_by_xpath('//div[@class="tc-drag-thumb"]')
        # 点击拖动按钮不放
        ActionChains(self.driver).click_and_hold(slider_bt).perform()
        # 按正向轨迹移动
        # move_by_offset函数是会延续上一步的结束的地方开始移动
        for i in track:
            ActionChains(self.driver).move_by_offset(xoffset=i, yoffset=0).perform()
            print(i)
            time.sleep(random.random() / 100)  # 每移动一次随机停顿0-1/100秒之间骗过了极验，通过率很高
        time.sleep(random.random())
        # 按逆向轨迹移动
        back_tracks = [-1, -0.5, -1]
        for i in back_tracks:
            time.sleep(random.random() / 100)
            ActionChains(self.driver).move_by_offset(xoffset=i, yoffset=0).perform()
        # 模拟人手抖动
        self.shake_mouse()
        time.sleep(random.random())
        # 松开滑块按钮
        ActionChains(self.driver).release().perform()


    def ffxivsign(self):
        self.driver.get("https://actff1.web.sdo.com/20180707jifen/#/home")
        time.sleep(1)
        self.driver.find_element_by_class_name("signBtn").click()
        time.sleep(1)
        self.driver.find_element_by_class_name("wegame_login_area").click()
        time.sleep(1)
        self.driver.switch_to.frame("ptlogin_iframe")
        time.sleep(1)
        self.driver.find_element_by_id("switcher_plogin").click()
        time.sleep(1)
        self.driver.find_element_by_id("u").send_keys("*********")  #账号
        time.sleep(1)
        self.driver.find_element_by_id("p").send_keys("*********")   #密码
        time.sleep(1)
        self.driver.find_element_by_id("login_button").click()
        time.sleep(1)
        self.driver.switch_to.default_content()
        time.sleep(1)
        select_type = self.driver.find_elements_by_class_name("el-input--suffix")
        time.sleep(1)
        if len(select_type) == 0:
            self.driver.switch_to.frame("ptlogin_iframe")
            self.driver.switch_to.frame("tcaptcha_iframe")
            time.sleep(3)
            src = self.driver.find_element_by_id("slideBg").get_attribute("src")
            img1, img2 = self.get_img(src)
            a = self.resize_img(img1)
            b = self.resize_img(img2)
            distance = self.get_gap_offset(a, b)
            track = self.get_track(distance)
            self.operate_slider(track)
        time.sleep(3)
        self.driver.switch_to.default_content()
        time.sleep(1)
        select_type = self.driver.find_elements_by_class_name("el-input--suffix")
        area_type = self.driver.find_elements_by_class_name("el-select-dropdown__item")
        time.sleep(1)
        select_type[0].click()
        time.sleep(1)
        area_type[1].click() # 选择大区
        time.sleep(3)
        select_type[1].click()
        time.sleep(2)
        area_type = self.driver.find_elements_by_class_name("el-select-dropdown__item")
        time.sleep(1)
        area_type[4].click() # 选择账号
        time.sleep(1)
        self.driver.find_element_by_class_name("el-button--primary").click()
        time.sleep(1)
        self.driver.find_element_by_class_name("eveBtn").click()
        time.sleep(1)
        print("签到成功")
        self.driver.close()


def bilibiliSign():
    url = 'https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign'
    #   header={'Host':host}
    headers = {
        'cookie': 'SESSDATA=*********', #b站cookie里面找到这个值替换掉***
        'Content-Type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 '
                      'Safari/537.36 '
    }
    req = requests.get(url, headers=headers)
    print(req.text)

if __name__ == '__main__':
    ffxiv  = Ffxivclass()
    ffxiv.ffxivsign()
    bilibiliSign()
