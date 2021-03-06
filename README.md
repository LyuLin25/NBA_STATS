# NBA_STATS

一、设计目标：
制作一个带NBA当前比分显示的及实时天气的时钟显示屏

二、设计过程：
（1）所用硬件：
	1、树莓派3（Model B）
	2、微雪4.3寸串口电子墨水屏
	3、DHT22温湿度传感器

（2）硬件连接：
	屏幕与树莓派的连接：
  墨水屏	DIN   	DOUT	  GND	 VCC
  树莓派	GPIO14	GPIO15	GND	 3.3V
	温湿度传感器与树莓派的连接：
  DHT22	   DOUT	 GND	 VCC
  树莓派	  BCM4	 GND	3.3V

（3）前期处理：
	经过查找资料了解到，树莓派3的硬件串口被分配给了蓝牙模块，而GPIO14和GPIO15的串口是	由内核模拟的，无法使用。
  所以要使用这两个串口，首先样将GPIO14和GPIO15改成硬件驱动。
	第一步 利用vim指令编辑 /boot/config.txt 在最后添加一行代码
	dtoverlay=pi3-miniuart-bt
	第二步 禁用自带的蓝牙
	sudo systemctl disable hciuart
	第三步 释放串口 编辑 /boot/cmdline.txt 将参数改成以下形式
	dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2
	rootfstype=ext4 	elevator=deadline fsck.repair=yes rootwait
	第四步 安装温湿度传感器的依赖
	git clone https://github.com/adafruit/Adafruit_Python_DHT.git
	cd Adafruit_Python_DHT
	sudo python ./setup.py install

（4）对串口屏的资源进行准备
	该串口屏对内部资源有以下要求：
	①字库
	系统内置32、48、64点阵的英文字库，在没有TF卡或者NandFlash的情况下都能正常使用；
  32、48、64点阵的中文字库，需要先将中文字库文件存入TF卡或者NandFlash中才能使用。
  ②图片显示
	图片支持1位、2位的位图格式，对于其他格式的图片，需要使用例程提供的软件工具先将图片转	换成指定格式就可以正常显示。
	图片的命名必须采用大写英文字符，并且文件名（包括.号） 长度不能超过10个字符。
	于是在串口屏的TF卡中准备了下图所示的文件：其中三个字母的图像表示的是各NBA球队的队标，大小为160x160像素左右；
  NUMX的图像是各个数码以及冒号的图案，大小为100x140像素。
  32、48、64点阵的中文GBK编码的字体点阵字库文件。
 	到此为止，前期的工作就基本完成了，可以进入代码编写的环节。

三、代码编写
（1）利用XPath命令到虎扑NBA获得当前的NBA比分数据。
	首先打开https://nba.hupu.com/，
 
	我们需要的比分内容就在红色框之中，利用开发者工具可以找到其中的内容，例如第一层中的雄鹿与	凯尔特人的比赛，比分是94：112，在下图中，已经找到网页源码中所对应的文字。
 
	通过拷贝各个项目的XPath就可以利用lxml库下的Xpath类得到其中的text内容，代码如下所示：
 
	在得到内容之后，将主队、客队与比分分别按相同的顺序已数组的方式存在各自的json文件中，以待	后面的读取。
	由于本人偏爱圣安东尼奥马刺队，仅关注本队的比分情况，所以我在完整的方案中选择在主队与客队	中搜索关键字“马刺”来获得马刺队的信息，并得到它是主场还是客场，对方球队的名字以及当前的	比分来在显示屏上进行显示，若进入无马刺队比赛，则在显示器上显示NO GAME TODAY的标志。
	其中使用了Python语法中数组中查找的命令（if '马刺' in Array）、在数组中定位的命令	（number = Array.index('马刺')），和在字典中查找内容的命令（dict_value = dict[name]）


（2）利用XPath进行实时温度的获取
	利用与上述同样的方法，可以在http://weather.sina.com.cn/中得到实时的数据并使用字典的格式写入	json文件，由于方	法类似，不加以叙述。

（3）利用DHT22温湿度传感器的输出信号得到当前室内测得的温度与湿度。
	由于已经安装了DHT22的库，故可以直接使用内部的read_retry命令来读取当前室内的温度和湿度	值，同时将读到的温度和湿度用字典的方式存在json文件中，以待读取。代码在下图所示。
 

（4）串口屏显示代码
	串口屏主要是利用三个命令来进行显示。
	①.text命令，它有三个参数X坐标，Y坐标和显示的内容。
		例如如下代码就是在(50, 390)的位置显示文字NO GAME。
screen.text(50, 390, 'NO GAME')
	②.bitmap命令，同样是三个参数，X坐标，Y坐标和显示的BMP的文件名。
		例如以下代码就是在(30, 250)的位置显示SAS.BMP图像
screen.bitmap(30, 250, 'SAS.BMP')
	③.line命令，有四个参数，起始点X坐标和Y坐标，终止点X坐标和Y坐标。
		例如以下代码就是画了一条从(0, 160)到(800, 160)的一条宽度为一像素的线段。
screen.line(0, clock_y + 160, 800, clock_y + 160)

（5）利用以上的代码进行整合就可以得到完整的显示NBA比分，由于代码较长，已添加在压缩包内。

四、代码的运行与维护
	在代码中使用了如下的循环判断命令，可以使得该程序可以无限循环的运行。
while True:
    if time.strftime('%S',time.localtime(time.time()))=='00' :
但仍旧存在一些问题，例如终端窗口需要一直保持打开，否则将会停止运行。
我找到了一个解决办法是利用Screen来保持窗口的后台持续运行，可以不需要一直打开该窗口。
