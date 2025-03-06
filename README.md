# Spotify Playlist Importer

一个将 Excel (.xls) 文件中的播放列表自动导入到 Spotify 账户的工具。这个项目主要用于学习编程知识，使用个人账号开发。

## 功能

- 从 Excel 文件读取歌曲信息
- 连接到 Spotify API
- 在 Spotify 中创建新播放列表
- 搜索歌曲并添加到播放列表中

## 技术栈

- Python
- pandas/openpyxl (Excel 处理)
- spotipy (Spotify API Python 客户端)

## 安装与使用

1. 克隆此仓库
2. 创建并激活虚拟环境:
   ```
   python -m venv venv
   source venv/bin/activate  # 在 Linux/macOS 上
   # 或
   venv\Scripts\activate  # 在 Windows 上
   ```
3. 安装依赖: `pip install -r requirements.txt`
4. 在 Spotify 开发者平台创建应用并获取 API 凭证
5. 配置 `.env` 文件，添加您的 Spotify API 凭证
6. 运行程序: `python import_playlist.py your_playlist.xls`

## 项目结构

```
import-playlist-learn/
├── import_playlist.py    # 主程序
├── spotify_client.py     # Spotify API 客户端
├── excel_reader.py       # Excel 文件读取器
├── requirements.txt      # 项目依赖
└── README.md             # 项目说明
```

## 待办事项

- [ ] 实现 Excel 文件读取
- [ ] 实现 Spotify API 连接
- [ ] 实现播放列表创建
- [ ] 实现歌曲搜索和添加
- [ ] 添加错误处理
- [x] 实现 Excel 文件读取
- [x] 实现 Spotify API 连接
- [x] 实现播放列表创建
- [x] 实现歌曲搜索和添加
- [x] 添加错误处理
- [ ] 添加用户界面（可选）
- [ ] 支持更多文件格式（如CSV）
- [ ] 添加单元测试
