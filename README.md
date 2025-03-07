# Spotify Playlist Importer

一个将播放列表文件自动导入到 Spotify 账户的工具。支持多种文件格式，包括 Excel、CSV、JSON 和文本文件。这个项目主要用于学习编程知识，使用个人账号开发。

## 功能

- 从多种格式的文件读取歌曲信息:
  - Excel 文件 (.xlsx, .xls, .xlsm)
  - CSV 文件 (.csv)
  - JSON 文件 (.json)
  - 文本文件 (.txt)
- 连接到 Spotify API
- 在 Spotify 中创建新播放列表（公开或私有）
- 导入到现有播放列表
- 设置播放列表封面图片
- 导出 Spotify 播放列表到 Excel
- 使用增强的搜索算法查找歌曲
- 交互式搜索，允许用户选择最佳匹配结果
- 导入前预览和编辑歌曲列表
- 搜索歌曲并添加到播放列表中
- 播放列表修正功能:
  - 删除播放列表中特定位置的歌曲
  - 交互式搜索并添加正确版本的歌曲
  - 增加搜索结果数量，提高匹配准确性
- 灵活处理非标准格式的文件:
  - 自定义列映射
  - 跳过文件开头的行数
  - 跳过空行或缺少必要信息的行
  - 自定义多首歌曲分隔符

## 文档

- [用户指南](docs/USER_GUIDE.md) - 详细的功能使用说明、示例和最佳实践
- [改进计划](IMPROVEMENT_PLAN.md) - 项目的改进计划和待办事项

## 技术栈

- Python
- pandas/openpyxl (Excel/CSV 处理)
- spotipy (Spotify API Python 客户端)
- json (JSON 处理)
- difflib (模糊匹配)

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
6. 运行程序: `python import_playlist.py your_playlist.xlsx`

更多详细使用说明，请参阅[用户指南](docs/USER_GUIDE.md)。

## 项目结构

```
import-playlist-learn/
├── import_playlist.py    # 主程序
├── spotify_client.py     # Spotify API 客户端
├── file_reader.py        # 文件读取器
├── export_playlist.py    # 播放列表导出工具
├── playlist_correction.py # 播放列表修正工具
├── create_examples.py    # 示例文件生成器
├── test_search.py        # 搜索功能测试工具
├── examples/             # 示例文件目录
├── docs/                 # 文档目录
│   └── USER_GUIDE.md     # 用户指南
├── requirements.txt      # 项目依赖
├── IMPROVEMENT_PLAN.md   # 改进计划
└── README.md             # 项目说明
```

## 待办事项

- [x] 实现 Excel 文件读取
- [x] 实现 Spotify API 连接
- [x] 实现播放列表创建
- [x] 实现歌曲搜索和添加
- [x] 添加错误处理
- [x] 支持更多文件格式（CSV、JSON、TXT）
- [x] 实现模糊匹配搜索算法
- [x] 添加用户选择搜索结果的功能
- [x] 添加私有/公开播放列表选项
- [x] 添加导入前预览功能
- [x] 支持导入到现有播放列表
- [x] 支持设置播放列表封面图片
- [x] 支持导出Spotify播放列表到Excel
- [x] 增强对非标准格式文件的处理
- [x] 支持删除播放列表中特定位置的歌曲
- [x] 支持交互式搜索并添加正确版本的歌曲
- [ ] 支持批量替换歌曲
- [ ] 添加用户界面（可选）
- [ ] 添加单元测试
