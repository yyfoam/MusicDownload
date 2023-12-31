# 音乐API 接口文档

## 概述

本文档提供了关于音乐API的详细和专业的**使用指南**。此API**支持**用户通过**发送**特定的**请求返回歌曲**、**专辑**或**视频转音频**的**下载链接，**该链接也可以在网页上**直接播放**。

## 设计初衷

为了提供一个**资源丰富**、涵盖几乎全网**音乐**的**解决方案**，使用户能够**轻松下载**和享受各种音乐。我意识到音乐的多样性和普遍需求，特别是在数字时代，人们对于获取音乐的便利性和速度有着更高的期待。因此，开发了这个API，它不仅能够满足个人用户的**日常娱乐**需求，而且还能为各种**应用场景**提供支持，如：**私人媒体库**、**机器人点歌台**等。我的目标是实现**听歌自由**，让每个人都能够**轻松访问**和**享受**他们喜爱的曲目，**不受限制**地**探索音乐**的广阔世界。

## 功能特点

它**提供**的**下载链接**已经完成了基本的**音乐元数据刮削**。这意味着下载的**音乐文件**不仅包含**高质量**的**音频**内容，还附带了**详细**的**元数据**信息。这些元数据包括歌曲的**标题、艺术家**、**专辑名称**、**专辑艺术家**、**发行年份**、**音轨号**、**碟号**等关键信息。此外，为了**提升音乐体验**，还加入了**音乐风格**、**作词人**、**作曲人**的信息，以及关键的视觉和文本元素，如**专辑封面**和**歌词**。这样的详尽元数据信息不仅**便于**用户对音乐文件的**管理**和**分类**，还丰富了用户的音乐欣赏过程，提供了更加**完整**和**沉浸式**的听歌**体验**。 

## API请求详情

### 基本信息

* **URL**: `https://www.yyfoam.top/music_api`
* **方法**: POST
* **请求格式**: JSON

### 请求参数

请求必须包含以下JSON格式的参数：

```json
{
  "from_uid": "用户自定义的唯一标识",
  "detail": {
    "content": "/song 歌曲名称 或 /album 专辑名称 或 /video 视频名称"
  },
  "sender": "url"
}

```

#### 参数说明

* `from_uid`: **用户自定义**的**唯一标识**。此参数用于标识请求者的身份，**必须具有唯一性**，以**防止**处理上的**混乱**或**错误**。
* `detail`: 包含请求的详细信息。
  * `content`: 指定下载内容的类型和名称。**可能**的类型**包括**：
    * `/song XXXX`：下载指定名称的**歌曲**。(速度**较快**)
    * `/album XXXX`：下载指定名称的**专辑**。（速度**较慢**）
    * `/video XXXX`：将**视频转换为歌曲**。使用此选项时应**注意**，**转换**得到的歌曲元数据**无法正常刮削**，并且音质可能较差。建议**仅在****`/song`**** 无法搜索到满意的结果时使用此方法**。 （速度**较快**）
* `sender`: 固定值 "url"。

## 注意事项

* 确保 `from_uid` 参数**必须具有唯一性**，**不要使用特殊字符**以避免处理错误。

* 使用 `/video` 选项时，存在**音质问题**和**无法刮削**元数据。

* **第一次调用**后**接口**会**记录反馈结果**，从而实现**交互**效果。

* **第二次**或**再次调用**时，确保`content`参数传入的是**上一次**响应数据中的**序号**如：**1**，或任意**合法请求** 如：**/song** XXXX 、 **/album** XXXX 、 **/video** XXXX **其中一项**。

* 目前**音乐元数据**来源为： **QQ**、**网易云**、**Spotify**等，如**上述平台没有**的元数据**无法刮削**。

* 如遇到**上述平台有**的数据，**依然无法刮削**的情况，请在名称后面**加上@en**，如歌曲：** **/song XXXX** @en ** **专辑同理**。

* PS:由于**音乐元数据刮削**是单独的**定时任务**，如果您发现下载的**音乐元数据不全**，如：**无歌词**，请**等一分钟**后**再次下载之前的链接**即可。

  ## 

## 实际请求和响应案例

### `/album` 请求示例

* 请求示例：/album Delight - The 2nd Mini Album

  ```json
  {
    "from_uid": "YYFOAM123456",
    "detail": {
      "content": "/album Delight - The 2nd Mini Album"
    },
    "sender": "url"
  }
  
  ```

* 第一次接口响应：返回详细信息供用户选择

  ```json
  { "msg": "1.(专辑):《Delight - The 2nd Mini Album》-伯贤-播放时长:None (2020)\n\n2.(专辑):《2nd Mini Album Whisper》-빅스LR VIXX LR-播放时长:None (2017)\n\n3.(专辑):《2nd MINI ALBUM》-유성은-播放时长:None (2015)\n\n4.(专辑):《The 2nd MINI ALBUM 'Love Loves To Love Love'》-Favorite-播放时长:None (2018)\n\n5.(专辑):《The Velvet - The 2nd Mini Album》-Red Velvet-播放时长:None (2016)\n\n6.(专辑):《Ambient Delight》-Meditation Relaxation Club-播放时长:None (2017)\n\n7.(专辑):《Pure Delight》-Pierrot Ensemble-播放时长:None (2012)\n\n8.(专辑):《秋のカフェでゆったり聴きたい音楽》-Musical Mogul-播放时长:None (2023)\n\n9.(专辑):《Music Feeling the Deepening of Autumn》-Musical Mogul-播放时长:None (2023)\n\n10.(专辑):《Cha Myung Hwa (Love Poem in Music Vol. 2)》-Cha Myung Hwa-播放时长:None (2014)\n\n\n\n 对结果不满意？\n\n帮助：搜索的歌曲或专辑及其歌手非华裔的请在搜索词后加上@en\n\n 例：/song Hotel California @en\n\n1.歌曲搜索: /song 歌曲名称 \n\n2.专辑搜索: /album 专辑名称 \n\n3.视频搜索: /video 视频名称 \n\nPS：/video 是在 音乐 和 专辑 都无法匹配到最佳结果的情况下再使用，因为视频转换音质可能较差。"} 
  
  ```

* 第二次请求和响应

  请求：用户选择序号 1

  ```json
  {
    "from_uid": "YYFOAM123456",
    "detail": {
      "content": "1"
    },
    "sender": "url"
  }
  
  ```

  响应：接口返回专辑《Delight - The 2nd Mini Album》的详细信息及下载链接

  ```json
  {
      "msg": {
          "Count": 7,
          "artist": "伯贤",
          "duration": "23分钟",
          "songs": {
              "Bungee": "https://www.yyfoam.top/music/FP_20240106221517_",
              "Candy": "https://www.yyfoam.top/music/FP_20231210225340_",
              "Ghost": "https://www.yyfoam.top/music/FP_20240106221617_",
              "Love Again": "https://www.yyfoam.top/music/FP_20240106221637_",
              "Poppin'": "https://www.yyfoam.top/music/FP_20240106221557_",
              "R U Ridin'?": "https://www.yyfoam.top/music/FP_20240106221456_",
              "Underwater": "https://www.yyfoam.top/music/FP_20240106221536_"
          },
          "title": "Delight - The 2nd Mini Album",
          "type": "专辑",
          "year": "2020"
      }
  }
  
  ```

### `/song` 请求示例

* 请求示例：/song 以父之名

  ```json
  {
    "from_uid": "YYFOAM123456",
    "detail": {
      "content": "/song 以父之名"
    },
    "sender": "url"
  }
  
  ```

* 第一次接口响应：返回详细信息供用户选择

  ```json
  {
   "msg": "1.(歌曲): 以父之名-周杰伦-《叶惠美》-播放时长:5:42 (None)\n\n2.(歌曲): 以父之名-周杰伦-《2004无与伦比演唱会》-播放时长:5:59 (None)\n\n3.(歌曲): 以父之名-周杰伦-《2010超时代演唱会》-播放时长:5:35 (None)\n\n4.(歌曲): 以父之名-周杰伦-《周杰伦地表最强世界巡回演唱会》-播放时长:3:45 (None)\n\n5.(歌曲): 夜的第七章-周杰伦-《依然范特西》-播放时长:3:48 (None)\n\n6.(歌曲): 以父之名-鹰响力-《鹰语浩瀚》-播放时长:4:23 (None)\n\n7.(歌曲): 以父之名-安眠音乐盒-《独处音乐|极致舒缓|听歌助眠》-播放时长:1:36 (None)\n\n8.(歌曲): 以父之名-Gill·吉尔-《以父之名》-播放时长:5:07 (None)\n\n9.(歌曲): 霍元甲-周杰伦-《霍元甲 EP》-播放时长:4:38 (None)\n\n10.(歌曲): 爷爷泡的茶-周杰伦-《八度空间》-播放时长:3:58 (None)\n\n11.(歌曲): 美人鱼-周杰伦-《周杰伦地表最强世界巡回演唱会》-播放时长:3:30 (None)\n\n12.(歌曲): 花海-周杰伦-《魔杰座》-播放时长:4:24 (None)\n\n13.(歌曲): 半岛铁盒-周杰伦-《八度空间》-播放时长:5:17 (None)\n\n14.(歌曲): 忍者-周杰伦-《The one 演唱会》-播放时长:2:52 (None)\n\n15.(歌曲): 无助-周杰伦-《天台 电影原声带》-播放时长:1:10 (None)\n\n16.(歌曲): 龙卷风-周杰伦-《杰伦》-播放时长:4:10 (None)\n\n17.(歌曲): 天台-周杰伦-《天台 电影原声带》-播放时长:1:46 (None)\n\n18.(歌曲): 我们全都有罪-谌宥-《我们全都有罪》-播放时长:5:04 (None)\n\n19.(歌曲): 跨时代-周杰伦-《2010超时代演唱会》-播放时长:3:11 (None)\n\n20.(歌曲): 东风破-周杰伦-《2010超时代演唱会》-播放时长:5:22 (None)\n\n\n\n 对结果不满意？\n\n帮助：搜索的歌曲或专辑及其歌手非华裔的请在搜索词后加上@en\n\n 例：/song Hotel California @en\n\n1.歌曲搜索: /song 歌曲名称 \n\n2.专辑搜索: /album 专辑名称 \n\n3.视频搜索: /video 视频名称 \n\nPS：/video 是在 音乐 和 专辑 都无法匹配到最佳结果的情况下再使用，因为视频转换音质可能较差。"
  } 
  
  ```

* 第二次请求和响应：

  请求：用户选择序号1

  ```json
  {
    "from_uid": "YYFOAM123456",
    "detail": {
      "content": "1"
    },
    "sender": "url"
  }
  
  ```

  响应：接口返回歌曲《以父之名》的下载链接

  ```json
  {
      "msg": {
          "song": "https://www.yyfoam.top/music/132071666"
      }
  }
  
  ```

### `/video` 请求示例

* 请求示例：/video 以父之名

  ```json
  {
    "from_uid": "YYFOAM123456",
    "detail": {
      "content": "/video 以父之名"
    },
    "sender": "url"
  }
  
  ```


* 第一次接口响应：

  ```json
  {
      "msg": "1.(视频): 以父之名-播放时长:6:04\n\n2.(视频): 以父之名 周杰伦 (歌词版)-播放时长:5:41\n\n3.(视频): 周杰伦暗黑三部曲，《以父之名》《夜的第七章》《止战之殇》-播放时长:14:30\n\n4.(视频): 以父之名 - 周杰伦（一小时版 One Hour）「仁慈的父我已坠入看不见罪的国度」-播放时长:1:01:31\n\n5.(视频): 【4K60FPS】周杰伦《以父之名》核能现场！天神下凡！ 音乐私藏馆-播放时长:5:39\n\n6.(视频): 【中国有嘻哈 EP12】吴亦凡 & PG ONE《以父之名》-播放时长:3:12\n\n7.(视频): 【周杰伦地表最强演唱会LIVE-以父之名】 Jay Chou's The Invincible Concert LIVE (In The Name of The Father)-播放时长:3:45\n\n8.(视频): 东尼大木最新力作--以父之名-播放时长:6:03\n\n9.(视频): 以父之名.avi-播放时长:5:01\n\n10.(视频): 【揉揉酱】翻奏 周杰伦《以父之名》【RouRouJ】Cover Jay Chou《In The Name of The Father》-播放时长:5:58\n\n11.(视频): 以父之名 周杰伦 动态鼓谱 ドラム楽谱-播放时长:5:43\n\n12.(视频): 【8·BIT纯享】周杰伦-以父之名-播放时长:5:00\n\n13.(视频): 周杰伦 - 以父之名 (伴奏)-播放时长:5:36\n\n14.(视频): 周杰伦 Jay Chou  - 以父之名 In The Name Of Father (HD Audio)-播放时长:5:43\n\n15.(视频): 【高音质】周杰伦-以父之名-播放时长:5:35\n\n16.(视频): Name of the father 以父之名 英文字幕-播放时长:6:02\n\n17.(视频): 以父之名 周杰伦 mp3 320kbps-播放时长:4:44\n\n18.(视频): 【周杰伦】2013魔天伦世界巡回演唱会 《手语+以父之名》-播放时长:9:23\n\n19.(视频): 以父之名-播放时长:3:49\n\n20.(视频): Jay Chou 周杰伦 《以父之名 | 》-播放时长:5:45\n\n\n\n 对结果不满意？\n\n帮助：搜索的歌曲或专辑及其歌手非华裔的请在搜索词后加上@en\n\n 例：/song Hotel California @en\n\n1.歌曲搜索: /song 歌曲名称 \n\n2.专辑搜索: /album 专辑名称 \n\n3.视频搜索: /video 视频名称 \n\nPS：/video 是在 音乐 和 专辑 都无法匹配到最佳结果的情况下再使用，因为视频转换音质可能较差。"
  } 
  
  ```

* 第二次请求和响应：

  请求：用户选择序号 1

  ```json
  {
    "from_uid": "YYFOAM123456",
    "detail": {
      "content": "1"
    },
    "sender": "url"
  }
  
  ```

  响应：接口返回转换后的音乐视频《以父之名》的下载链接（实际为MP3）

  ```json
  {
      "msg": {
          "video": "https://www.yyfoam.top/music/FP_20240106233827_"
      }
  }
  
  ```

## 联系方式

如您在使用音乐API接口过程中有任何**疑问**或需要**技术支持**，或有更好的**建议**和**意见**等，欢迎通过**微信**:**`yyfoam`**或**邮箱**:**`yyfoam@hotmail.com`**联系。我将尽力提供帮助，确保您的使用体验尽可能顺畅和高效。无论是对接口的**疑问**、**功能请求**还是**问题反馈**，都**非常欢迎**。

## PS:`demo.py`为核心下载代码，不带音乐元数据刮削功能.
