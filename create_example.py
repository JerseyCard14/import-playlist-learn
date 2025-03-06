#!/usr/bin/env python3
import pandas as pd

# 创建示例数据
data = {
    'song_name': [
        'Shape of You', 
        'Blinding Lights', 
        'Dance Monkey', 
        'Someone You Loved', 
        'Watermelon Sugar',
        '七里香',
        '晴天',
        'Dynamite',
        'Bad Guy',
        'Uptown Funk'
    ],
    'artist': [
        'Ed Sheeran', 
        'The Weeknd', 
        'Tones and I', 
        'Lewis Capaldi', 
        'Harry Styles',
        '周杰伦',
        '周杰伦',
        'BTS',
        'Billie Eilish',
        'Mark Ronson ft. Bruno Mars'
    ]
}

# 创建DataFrame
df = pd.DataFrame(data)

# 保存为Excel文件
df.to_excel('example_playlist.xlsx', index=False)

print("示例播放列表已创建: example_playlist.xlsx") 