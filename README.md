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
- 使用增强的搜索算法查找歌曲
- 交互式搜索，允许用户选择最佳匹配结果
- 导入前预览和编辑歌曲列表
- 搜索歌曲并添加到播放列表中

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

### 命令行选项

```
usage: import_playlist.py [-h] [--name NAME] [--description DESCRIPTION] [--private] [--verbose] [--preview] [--no-preview] [--interactive] file

将播放列表文件导入到Spotify

positional arguments:
  file                  播放列表文件路径 (支持 Excel, CSV, JSON, TXT 格式)

optional arguments:
  -h, --help            显示帮助信息并退出
  --name NAME, -n NAME  播放列表名称（可选，默认使用文件中的名称或文件名）
  --description DESCRIPTION, -d DESCRIPTION
                        播放列表描述（可选）
  --private, -p         创建私有播放列表（默认为公开）
  --verbose, -v         显示详细信息
  --preview, -P         导入前预览歌曲列表
  --no-preview          跳过预览直接导入
  --interactive, -i     启用交互式搜索（允许用户选择搜索结果）
```

### 预览功能

当歌曲数量超过5首时，程序默认会显示预览界面，您可以在导入前查看和编辑歌曲列表：

- 查看所有歌曲
- 删除不需要的歌曲
- 添加新歌曲
- 编辑现有歌曲
- 测试搜索特定歌曲

您也可以使用 `--preview` 选项强制显示预览，或使用 `--no-preview` 选项跳过预览直接导入。

### 交互式搜索

使用 `--interactive` 或 `-i` 选项启用交互式搜索功能。当搜索歌曲时，如果找到多个匹配结果，程序会显示这些结果并让您选择最合适的一个：

```
为 'Shape of You' - Ed Sheeran 找到多个结果:
1. Shape of You - Ed Sheeran (÷ (Deluxe))
2. Shape of You - Ed Sheeran (÷)
3. Shape of You - Ed Sheeran (Shape of You)
4. Shape of You - Acoustic - Ed Sheeran (Shape of You (Acoustic))
5. Shape of You - Major Lazer Remix - Ed Sheeran (Shape of You (Major Lazer Remix))

请选择一个结果 (1-5), 或输入 'n' 跳过:
```

这对于处理有多个版本的歌曲或名称相似的歌曲特别有用。

### 测试搜索功能

您可以使用 `test_search.py` 脚本测试增强的搜索功能:

```
python test_search.py "歌曲名" --artist "艺术家名" --verbose
```

或者使用交互式搜索:

```
python test_search.py "歌曲名" --artist "艺术家名" --interactive
```

## 增强的搜索算法

本工具使用多种搜索策略来提高歌曲匹配率:

1. **文本清理和标准化** - 移除括号内容、特殊字符和多余空格
2. **多策略搜索** - 按顺序尝试多种搜索方法:
   - 精确搜索 (歌曲名 + 艺术家)
   - 仅歌曲名搜索
   - 关键词搜索 (不使用field限定符)
   - 分词搜索 (处理歌曲名可能包含艺术家的情况)
   - 模糊匹配搜索 (获取多个结果并比较相似度)
3. **相似度评分** - 使用序列匹配算法计算相似度得分
4. **用户选择** - 在交互式模式下，允许用户从多个搜索结果中选择最佳匹配

## 支持的文件格式

### Excel 文件 (.xlsx, .xls, .xlsm)
需要包含 `song_name` 和 `artist` 列。

### CSV 文件 (.csv)
需要包含 `song_name` 和 `artist` 列。

### JSON 文件 (.json)
支持两种格式:
1. 歌曲列表格式:
   ```json
   [
     {"song_name": "歌曲1", "artist": "艺术家1"},
     {"song_name": "歌曲2", "artist": "艺术家2"}
   ]
   ```

2. 对象格式:
   ```json
   {
     "name": "播放列表名称",
     "songs": [
       {"song_name": "歌曲1", "artist": "艺术家1"},
       {"song_name": "歌曲2", "artist": "艺术家2"}
     ]
   }
   ```

### 文本文件 (.txt)
每行一首歌，格式为 `歌曲名 - 艺术家`。
第一行如果以 `# ` 开头，将被视为播放列表名称。

## 生成示例文件

运行 `python create_examples.py` 可以生成各种格式的示例文件，用于测试。

## 项目结构

```
import-playlist-learn/
├── import_playlist.py    # 主程序
├── spotify_client.py     # Spotify API 客户端
├── file_reader.py        # 文件读取器
├── create_examples.py    # 示例文件生成器
├── test_search.py        # 搜索功能测试工具
├── examples/             # 示例文件目录
├── requirements.txt      # 项目依赖
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
- [ ] 添加用户界面（可选）
- [ ] 添加单元测试
