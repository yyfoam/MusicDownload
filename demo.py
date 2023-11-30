import os
import re
import pytz
import html
import eyed3
import imghdr
import yt_dlp
import opencc
import requests
import datetime
from mutagen import File
from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
from selenium import webdriver
from eyed3.id3.frames import ImageFrame


# 音乐搜索
class Search:
    # 固定方法 决不能改 需要配合Bot
    query_result = {
        'select_type': 0,  # 默认0：检索失败 1:检索成功需要选择
        'data': ''  # 反馈给客户端的消息
    }
    song = 'song'  # 歌曲
    video = 'video'  # 视频
    album = 'album'  # 专辑
    artist = 'artist'  # 艺术家

    def __init__(self, key, query_type, language='zh_CN'):
        self.search = key  # 关键字
        self.data = {}  # 筛选整理后的源数据
        self.query_type = query_type  # 查询类型
        self.language = language
        self.sid = ''
        # 创建一个空字典来存储所有歌曲信息

    def __call__(self, *args, **kwargs):
        self.query_result = {
            'select_type': 0,  # 默认0：检索失败 1:检索成功需要选择
            'data': ''  # 反馈给客户端的消息
        }
        self.retrieve_and_organize_data()  # 检索并整理数据

    # 检索并整理数据
    def retrieve_and_organize_data(self):
        yt = YTMusic(language=self.language)  # 创建一个YTMusic对象
        search_results = yt.search(self.search, filter=self.query_type + 's')  # 搜索传过来的类型

        temp = []
        # 创建一个转换器，从繁体中文到简体中文
        converter = opencc.OpenCC('t2s')
        for i in search_results:
            if i['resultType'] in (self.song, self.video, self.album, self.artist):
                temp.append(i)
        if temp:
            self.query_result['select_type'] = 1
        count = 1
        for i in temp:
            if i['resultType'] == self.song:
                title = i.get('title')
                artist = i.get('artists', [])  # 获取 'artists' 键对应的列表，如果不存在则返回空列表
                if artist:  # 检查列表是否为空
                    artist = artist[-1].get('name', '')  # 获取第一个艺术家的名字，如果不存在则返回空字符串
                else:
                    artist = ''
                try:
                    album = i.get('album').get('name')
                except AttributeError:
                    album = ''
                duration = i.get('duration')
                year = i.get('year')
                t = f"{count}.(歌曲): {title}-{artist}-《{album}》-播放时长:{duration} ({year})\n\n"
                t = converter.convert(t)
                i['select_type'] = self.query_type
                i['language'] = self.language
                self.data[str(count)] = i  # 需要交互操作的数据单独存
                self.query_result['data'] += t
                count += 1
            elif i['resultType'] == self.video:
                title = i.get('title')
                duration = i.get('duration')
                t = f"{count}.(视频): {title}-播放时长:{duration}\n\n"
                t = converter.convert(t)
                i['select_type'] = self.query_type
                i['language'] = self.language
                self.data[str(count)] = i  # 需要交互操作的数据单独存
                self.query_result['data'] += t
                count += 1
            elif i['resultType'] == self.album:
                try:
                    t = f"{count}.(专辑):《{i['title']}》" \
                        f"-{[ii['name'] for ii in i['artists']][-1]}-播放时长:{i['duration']} ({i['year']})\n\n"
                except KeyError:
                    t = f"{count}.(艺术家): {[ii['name'] for ii in i['artists']][-1]}\n\n"
                t = converter.convert(t)
                i['select_type'] = self.query_type
                i['language'] = self.language
                self.data[str(count)] = i  # 需要交互操作的数据单独存
                self.query_result['data'] += t
                count += 1
            elif i['resultType'] == self.artist:
                try:
                    t = f"{count}.(艺术家): “{i['artists'][-1]['name']}” {i['subscribers']}\n\n"
                except KeyError:
                    t = f"{count}.(个人资料): {i['artist']}\n\n"
                count += 1
                t = converter.convert(t)
                i['select_type'] = self.query_type
                i['language'] = self.language
                self.data[str(count)] = i  # 需要交互操作的数据单独存
                self.query_result['data'] += t


# 下载数据数据
class Download:
    # 固定方法  需要配合Bot
    query_result = {
        'select_type': 0,  # 默认0：检索失败 1:检索成功需要选择
        'data': ''  # 反馈给客户端的消息
    }

    def __init__(self, url=''):
        self.get_url = url
        self.html_file = ''  # 获取到的html
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument("--lang=zh-CN")
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')
        # 获取当前脚本所在的目录
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.current_directory)

        # 存储新的专辑和单曲的链接
        self.new_releases_link_dict = {}
        # 存储音乐链接
        self.music_link_dict = {}
        # 专辑信息(专辑下载时用)
        self.album_info = {
            'AlbumImg': '',  # 专辑封面
            'AlbumName': '',  # 专辑名称
            'AlbumArtist': '',  # 专辑艺术家
            'AlbumYears': '',  # 专辑年份
            'AlbumType': '',  # 专辑类型
        }
        # 歌曲元数据信息（歌曲下载时用）
        self.song_info = {
            '标题': '',
            '艺术家': '',
            '专辑': '',
            '专辑艺术家': '',
            '年份': '',
            '音轨号': '',
            '碟号': '',
            '风格': '',
            '作曲': '',
            '作词': '',
            '歌词': '',
            '封面': ''
        }
        # 主键（音乐保存路径）
        self.sid = ''

    def __call__(self, *args, **kwargs):
        self.query_result = {
            'select_type': 0,  # 默认0：检索失败 1:检索成功需要选择
            'data': ''  # 反馈给客户端的消息
        }
        self.get_html()

    # 获取html
    def get_html(self):
        # 创建Chrome WebDriver实例
        driver = webdriver.Chrome(options=self.chrome_options)
        # 打开网站
        driver.get(self.get_url)
        # 获取当前网页的URL
        self.html_file = driver.page_source
        # 关闭浏览器
        driver.quit()

    # 解析获取的所有的新专辑及单曲的html 获得单个专辑的url地址（仅限于打开后全是专辑的页面）
    def parse_new_releases_html(self):
        self.new_releases_link_dict = {}  # 初始化一下！
        # 使用正则表达式提取链接和文本
        pattern = r'href="browse/(.*?)"[^>]*?>(.*?)<\/a>'
        matches = re.findall(pattern, self.html_file)
        for match in matches:
            link_url = match[0]
            link_text = html.unescape(match[1])
            self.new_releases_link_dict[link_text] = home_url + 'browse/' + link_url
            # print(link_text, link_url)

    # 解析单张专辑的html 得到download url
    def parse_albums_html(self):
        self.music_link_dict = {}  # 初始化一下！
        self.get_album_info(self.html_file)  # 通过html获取专辑信息
        # 使用正则表达式提取歌曲链接
        music_pattern = r'href="watch\?(.*?)"[^>]*?>(.*?)<\/a>'
        music_matches = re.findall(music_pattern, self.html_file)
        for match in music_matches:
            link_url = match[0].split('&')[0]  # 去掉&amp;及其后面的部分
            link_text = html.unescape(match[1])
            self.music_link_dict[link_text] = video_url + 'watch?' + link_url
            # print(video_url + 'watch?' + link_url)

    # 通过html获取专辑信息
    def get_album_info(self, html_content):
        self.album_info = {}
        # 专辑图像
        album_img_pattern = re.compile(
            r'<div id="thumbnail"[^>]*>.*?<img[^>]*id="img".*?src="(.*?)".*?</div>', re.DOTALL
        )
        self.album_info['AlbumImg'] = html.unescape(album_img_pattern.findall(html_content)[0])
        # 专辑名称
        album_name_pattern = r'<h2[^>]*?>\s*?<yt-formatted-string[^>]*?>(.*?)<\/yt-formatted-string>\s*?<\/h2>'
        self.album_info['AlbumName'] = html.unescape(re.findall(album_name_pattern, html_content, re.DOTALL)[0])
        # 专辑艺术家
        album_artist_pattern = r'<yt-formatted-string class="subtitle.*? dir="auto">(.*?)</a><span dir="auto"'
        self.album_info['AlbumArtist'] = html.unescape(re.findall(album_artist_pattern, html_content, re.DOTALL)[0])

        # 专辑年份
        album_years_pattern = 'href="channel/.*?</span><span dir="auto" class="style-scope ' \
                              'yt-formatted-string">(.*?)</span></yt-formatted-string>'
        self.album_info['AlbumYears'] = html.unescape(re.findall(album_years_pattern, html_content, re.DOTALL)[0])
        # 专辑类型
        album_type_pattern = r'<yt-formatted-string class="subtitle style-scope ytmusic-detail-header-renderer"' \
                             r' split-lines=""><span dir="auto" class="style-scope yt-formatted-string">(.*?)</span>'
        self.album_info['AlbumType'] = html.unescape(re.findall(album_type_pattern, html_content, re.DOTALL)[0])

        if self.album_info['AlbumType'] == 'Single':
            self.album_info['AlbumName'] = self.album_info['AlbumName'] + ' - ' + self.album_info['AlbumType']
        elif self.album_info['AlbumType'] == 'EP':
            self.album_info['AlbumName'] = self.album_info['AlbumName'] + ' ' + self.album_info['AlbumType']

    # 通过html获取歌手信息
    def get_artist(self):
        artist_pattern = r'<ytmusic-responsive-list-item-renderer.*?">(.*?)</ytmusic-responsive-list-item-renderer>'
        song_hh = html.unescape(re.findall(artist_pattern, self.html_file, re.DOTALL))
        name = r'<a class="yt-simple-endpoint style-scope yt-formatted-string".*?>(.*?)</a>'
        temp = {}
        for i in song_hh:
            s_info = html.unescape(re.findall(name, i, re.DOTALL))
            temp[s_info[0]] = '/'.join(s_info[1::])
        return temp

    # 下载专辑 参数：{专辑名称：下载链接}
    def download_album(self, album_links_dict):
        send_data = ''
        for k, v in album_links_dict.items():
            print(datetime.datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S"), f'正在下载专辑：{k}', v)
            try:
                self.get_url = v  # 初始化url
                self.__call__()
                self.parse_albums_html()
                artists = self.get_artist()  # 里面会有专辑下每首歌的艺术家 字典
                long = len(self.music_link_dict)  # 专辑 歌曲数量
                count = 0  # 歌曲序号
                print(datetime.datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S"), '下载的专辑信息：', self.album_info)
                converter = opencc.OpenCC('t2s')  # 繁转简
                for key, value in self.music_link_dict.items():
                    print(datetime.datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S"), '发送：', key, value)
                    count += 1
                    if artists.get(key):
                        artist = converter.convert(artists[key])
                    else:
                        artist = converter.convert(self.album_info['AlbumArtist'])
                    album_artist = converter.convert(self.album_info['AlbumArtist'])
                    title = converter.convert(key)
                    album = converter.convert(self.album_info['AlbumName'])
                    self.song_info['标题'] = title
                    self.song_info['艺术家'] = artist
                    self.song_info['专辑艺术家'] = album_artist
                    self.song_info['专辑'] = album
                    self.song_info['年份'] = self.album_info['AlbumYears']
                    pattern = re.compile(r'=w.*')
                    img_url = re.sub(pattern, '', self.album_info['AlbumImg']) + '=w1200-h1200'
                    self.song_info['封面'] = img_url
                    # 开始下载
                    self.download_song({key: value}, count, long)
                    # 初始化
                    self.song_info = {
                        '标题': '',
                        '艺术家': '',
                        '专辑': '',
                        '专辑艺术家': '',
                        '年份': '',
                        '音轨号': '',
                        '碟号': '',
                        '风格': '',
                        '作曲': '',
                        '作词': '',
                        '歌词': '',
                        '封面': ''
                    }
            except IndexError:
                send_data = f'专辑：{k} 下载失败！'
            self.query_result['data'] = send_data

    # 下载歌曲 参数：{歌曲名称：下载链接}， 歌名， 艺术家， 专辑  可选参数:音轨号 专辑音乐总数
    def download_song(self, music_link_dict, track_num_count=0, track_num_long=0):
        for key, value in music_link_dict.items():
            print(datetime.datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S"), '处理:', {key: value})
            # self.get_music_metadata(title, artist, album)       # 通过其他平台获取音乐元数据
            # 专辑路径
            music_file_path = os.path.join(self.current_directory, f"{music_path}/{self.song_info['专辑']}")
            os.makedirs(music_file_path, exist_ok=True)  # 自动创建文件夹
            os.chmod(music_file_path, 0o777)
            # 歌词临时路径
            subtitles_file_path = os.path.join(self.current_directory, f"{subtitles_temp}")
            os.makedirs(subtitles_file_path, exist_ok=True)  # 自动创建文件夹

            # 保存图像
            img_file_path = f'{music_file_path}/folder.jpg'  # 封面保存路径
            if not os.path.exists(img_file_path):  # 不存在才下载
                response = requests.get(self.song_info['封面'])  # 访问专辑封面
                if response.status_code == 200:
                    # 图像的二进制数据
                    image_data = response.content
                    # 保存图像到本地
                    with open(img_file_path, 'wb') as image_file:
                        image_file.write(image_data)
            # 开始下载
            _file = datetime.datetime.now(china_tz).strftime("%Y%m%d%H%M%S")
            file = _file + '.mp3'
            _music_path = f"{music_file_path}/{_file}"
            music_to_path = f"{music_file_path}/{file}"
            # 创建一个YoutubeDL对象
            music_ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'outtmpl': _music_path  # 设置文件保存路径和名称模板
            }
            music_ydl = YoutubeDL(music_ydl_opts)
            try:
                # 下载并转换为MP3格式
                music_ydl.download([value])
            except yt_dlp.utils.DownloadError:
                return
            # 打开音乐文件
            audio = eyed3.load(music_to_path)
            print(datetime.datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S"), '歌曲信息：', self.song_info)
            # 修改标题
            audio.tag.title = self.song_info['标题']
            # 修改艺术家
            audio.tag.artist = self.song_info['艺术家']
            # 修改专辑
            audio.tag.album = self.song_info['专辑']
            # 修改专辑艺术家
            if self.song_info['专辑艺术家']:
                album_artist = self.song_info['专辑艺术家'].strip()
            else:
                album_artist = self.song_info['艺术家']
            audio.tag.album_artist = album_artist
            try:
                if track_num_count != 0 and track_num_long != 0:
                    track_num_start = track_num_count
                    track_num_end = track_num_long
                else:
                    track_num_start = int(self.song_info['音轨号'])
                    track_num_end = None
            except ValueError:
                track_num_start = 1
                track_num_end = None
            audio.tag.track_num = (track_num_start, track_num_end)  # (当前音轨号, 总音轨数) 默认为1
            # 处理封面
            if os.path.exists(img_file_path):
                # 打开封面图像文件
                img_ = imghdr.what(img_file_path)
                img_save = open(img_file_path, 'rb').read()
                # 将图像添加到MP3文件中
                audio.tag.images.set(ImageFrame.FRONT_COVER, img_save, 'image/' + img_)

                img_debug = os.path.dirname(music_to_path)  # img路径debug：用歌曲绝对路径的上一级目录
                img_debug_path = f'{img_debug}/folder.jpg'  # 封面绝对路径修复bug
                # 如果没有的话 保存图像
                if not os.path.exists(img_debug_path):
                    with open(img_debug_path, 'wb') as image_file:
                        image_file.write(img_save)
            # 修改歌词
            audio.tag.lyrics.set(self.song_info['歌词'])
            # 保存更改
            audio.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding="utf-8")
            audio_file = File(music_to_path, easy=True)
            audio_file["genre"] = re.sub('&amp;', '&', self.song_info['风格'])
            disc_number = str(self.song_info['碟号']).strip()
            if disc_number and int(disc_number) >= 1:
                disc_num_start = disc_number
            else:
                disc_num_start = '1'
            audio_file['discnumber'] = disc_num_start
            # 修改作曲家
            audio_file['composer'] = self.song_info['作曲']
            # 修改作词家
            audio_file['lyricist'] = self.song_info['作词']
            audio_file["date"] = self.song_info['年份']
            # 保存更改
            audio_file.save()
            os.chmod(music_to_path, 0o777)
            print(datetime.datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S"), '下载完成：', self.song_info)
            # 初始化
            self.song_info = {
                '标题': '',
                '艺术家': '',
                '专辑': '',
                '专辑艺术家': '',
                '年份': '',
                '音轨号': '',
                '碟号': '',
                '风格': '',
                '作曲': '',
                '作词': '',
                '歌词': '',
                '封面': ''
            }


# 下载音乐（互动）
def download_song(data):
    print(data)
    converter = opencc.OpenCC('t2s')
    # 视频或音乐可以生成直接下载链接
    download_url = f"{video_url}watch?v={data['videoId']}"
    download = Download()
    try:
        title = converter.convert(data.get('title'))
        artist = data.get('artists')  # 艺术家
        if artist:  # 检查列表是否为空
            artist = converter.convert('\\'.join(artist['name'] for artist in data['artists']))
        else:
            artist = ''
        album = converter.convert(data.get('album').get('name'))  # 专辑
        img = data.get('thumbnails')[-1].get('url')
        pattern = re.compile(r'=w.*')
        img_url = re.sub(pattern, '', img) + '=w1200-h1200'  # 图像

        # 默认用youtube的 标题
        download.song_info['标题'] = title
        download.song_info['艺术家'] = artist
        download.song_info['专辑'] = album
        download.song_info['封面'] = img_url
        print(title, artist, album)
        # 下载开始
        download.download_song({title: download_url})
        download.query_result['data'] = f'下载完成：{title} \n'
    except Exception as f:
        print(f)
        download.query_result['data'] = f"{converter.convert(data.get('title'))}: 下载失败！{str(f)}\n"

    return download.query_result['data']


# 下载视频
def download_video(data):
    album_pending = 'Video to Music'  # 区分没有专辑名称的关键字
    img_url = 'https://cloud.yyfoam.top/f/d0db8c9338fe4921982e/?dl=1'  # 默认封面
    print(data)
    converter = opencc.OpenCC('t2s')
    # 视频或音乐可以生成直接下载链接
    download_url = f"{video_url}watch?v={data['videoId']}"
    download = Download()
    try:
        title = converter.convert(data.get('title'))
        artist = data.get('artists', '')  # 获取 'artists' 键对应的列表，如果不存在则返回空列表
        if artist:  # 检查列表是否为空
            artist = converter.convert(artist[0].get('name', ''))  # 获取第一个艺术家的名字，如果不存在则返回空字符串
        else:
            artist = ''
        try:
            album = converter.convert(data.get('album').get('name'))
        except AttributeError:
            album = album_pending
            download.song_info['专辑艺术家'] = 'YYFOAM'
        if album != album_pending:
            img = data.get('thumbnails')[-1].get('url')
            pattern = re.compile(r'=w.*')
            img_url = re.sub(pattern, '', img) + '=w1200-h1200'

        # 默认用youtube的 标题
        download.song_info['标题'] = title
        download.song_info['艺术家'] = artist
        download.song_info['专辑'] = album
        download.song_info['封面'] = img_url
        print(title, artist, album)
        # 下载开始
        download.download_song({title: download_url})
        download.query_result['data'] = f'下载完成：{title} \n'
    except Exception as f:
        print(f)
        download.query_result['data'] = f"{converter.convert(data.get('title'))}: 下载失败！{str(f)}\n"

    return download.query_result['data']


# 默认参数
home_url = 'https://music.youtube.com/'  # 音乐地址
video_url = 'https://www.youtube.com/'  # 视频地址

"""以下为自定义内容"""
china_tz = pytz.timezone('Asia/Shanghai')  # 时区
# 保存路径（音频文件）
subtitles_temp = 'subtitles'  # 歌词临时文件夹 (未使用)
music_path = 'test'  # 保存路径

if __name__ == '__main__':
    search_type = {
        1: 'song',  # 歌曲
        2: 'video',  # 视频
        3: 'album',  # 专辑
        4: 'artist'  # 艺术家(自己写！)
    }

    # 歌曲下载示例
    def song_test():
        text = '浪漫手机 周杰伦'
        run = Search(text, search_type[1])
        run()
        send = ''
        for key_, value_ in run.query_result.items():
            # 检查值是否为字符串类型
            if isinstance(value_, str):
                # 将字符串信息添加到列表中
                send += value_ + '\n'
        print(send)  # 发送给用户看的
        index = str(input('请选择要下载的音乐\n'))
        print(run.data[index])  # 丢给下载方法的数据
        send = download_song(run.data[index])
        print(send)
    song_test()

    # 专辑下载示例
    def album_test():
        text = '浪漫手机 周杰伦'
        run = Search(text, search_type[3])
        run()
        send = ''
        for key_, value_ in run.query_result.items():
            # 检查值是否为字符串类型
            if isinstance(value_, str):
                # 将字符串信息添加到列表中
                send += value_ + '\n'
        print(send)  # 发送给用户看的
        index = str(input('请选择要下载的专辑\n'))
        print(run.data[index])  # 丢给下载方法的数据
        browseId = run.data[index]['browseId']
        url = f"{home_url}channel/{browseId}"
        name = run.data[index]['title']
        download_data = {name: url}
        run = Download()
        run.download_album(download_data)
        print(run.query_result['data'])
    album_test()

    # 视频转音频示例
    def video_test():
        text = '浪漫手机 周杰伦'
        run = Search(text, search_type[2])
        run()
        send = ''
        for key_, value_ in run.query_result.items():
            # 检查值是否为字符串类型
            if isinstance(value_, str):
                # 将字符串信息添加到列表中
                send += value_ + '\n'
        print(send)  # 发送给用户看的
        index = str(input('请选择要下载的视频\n'))
        data = run.data[index]
        send = download_video(data)
        print(send)
    video_test()