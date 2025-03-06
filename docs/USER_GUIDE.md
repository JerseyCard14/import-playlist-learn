# Spotify Playlist Importer 用户指南

本文档提供了 Spotify Playlist Importer 工具的详细使用说明，包括各种功能的使用方法、示例和最佳实践。

## 目录

- [基本使用](#基本使用)
- [文件格式支持](#文件格式支持)
- [命令行选项](#命令行选项)
- [交互式搜索](#交互式搜索)
- [预览和编辑功能](#预览和编辑功能)
- [处理非标准格式文件](#处理非标准格式文件)
- [导入到现有播放列表](#导入到现有播放列表)
- [设置播放列表封面](#设置播放列表封面)
- [导出播放列表](#导出播放列表)
- [测试搜索功能](#测试搜索功能)
- [常见问题解答](#常见问题解答)
- [高级使用技巧](#高级使用技巧)

## 基本使用

### 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/your-username/import-playlist-learn.git
   cd import-playlist-learn
   ```

2. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在 Linux/macOS 上
   # 或
   venv\Scripts\activate  # 在 Windows 上
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 配置 Spotify API

1. 访问 [Spotify 开发者平台](https://developer.spotify.com/dashboard/)，创建一个应用
2. 获取 Client ID 和 Client Secret
3. 在应用设置中添加重定向 URI：`http://localhost:8888/callback`
4. 创建 `.env` 文件，添加以下内容：
   ```
   SPOTIPY_CLIENT_ID=your_client_id
   SPOTIPY_CLIENT_SECRET=your_client_secret
   SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
   ```

### 基本导入命令

最简单的导入命令：

```bash
python import_playlist.py your_playlist.xlsx
```

这将读取 Excel 文件中的歌曲信息，创建一个新的公开播放列表，并添加找到的歌曲。

## 文件格式支持

### Excel 文件 (.xlsx, .xls, .xlsm)

Excel 文件需要包含 `song_name` 和 `artist` 列。如果列名不同，可以使用列映射选项（见[处理非标准格式文件](#处理非标准格式文件)）。

**标准格式示例：**

| song_name       | artist      |
| --------------- | ----------- |
| Shape of You    | Ed Sheeran  |
| Blinding Lights | The Weeknd  |
| Dance Monkey    | Tones and I |

**导入命令：**
```bash
python import_playlist.py playlist.xlsx
```

### CSV 文件 (.csv)

CSV 文件需要包含 `song_name` 和 `artist` 列。

**标准格式示例：**
```csv
song_name,artist
Shape of You,Ed Sheeran
Blinding Lights,The Weeknd
Dance Monkey,Tones and I
```

**导入命令：**
```bash
python import_playlist.py playlist.csv
```

### JSON 文件 (.json)

支持两种 JSON 格式：

**1. 歌曲列表格式：**
```json
[
  {"song_name": "Shape of You", "artist": "Ed Sheeran"},
  {"song_name": "Blinding Lights", "artist": "The Weeknd"},
  {"song_name": "Dance Monkey", "artist": "Tones and I"}
]
```

**2. 对象格式（带播放列表名称）：**
```json
{
  "name": "我的播放列表",
  "songs": [
    {"song_name": "Shape of You", "artist": "Ed Sheeran"},
    {"song_name": "Blinding Lights", "artist": "The Weeknd"},
    {"song_name": "Dance Monkey", "artist": "Tones and I"}
  ]
}
```

**导入命令：**
```bash
python import_playlist.py playlist.json
```

### 文本文件 (.txt)

文本文件中每行一首歌，格式为 `歌曲名 - 艺术家`。第一行如果以 `# ` 开头，将被视为播放列表名称。

**标准格式示例：**
```
# 我的播放列表
Shape of You - Ed Sheeran
Blinding Lights - The Weeknd
Dance Monkey - Tones and I
```

**导入命令：**
```bash
python import_playlist.py playlist.txt
```

## 命令行选项

### 基本选项

| 选项                        | 简写             | 描述                           |
| --------------------------- | ---------------- | ------------------------------ |
| `--name NAME`               | `-n NAME`        | 指定播放列表名称               |
| `--description DESCRIPTION` | `-d DESCRIPTION` | 指定播放列表描述               |
| `--private`                 | `-p`             | 创建私有播放列表（默认为公开） |
| `--verbose`                 | `-v`             | 显示详细信息                   |

**示例：**
```bash
python import_playlist.py playlist.xlsx -n "我的播放列表" -d "我最喜欢的歌曲集合" -p -v
```

### 预览选项

| 选项           | 简写 | 描述               |
| -------------- | ---- | ------------------ |
| `--preview`    | `-P` | 导入前预览歌曲列表 |
| `--no-preview` |      | 跳过预览直接导入   |

**示例：**
```bash
python import_playlist.py playlist.xlsx --preview
```

### 搜索选项

| 选项            | 简写 | 描述                                   |
| --------------- | ---- | -------------------------------------- |
| `--interactive` | `-i` | 启用交互式搜索（允许用户选择搜索结果） |

**示例：**
```bash
python import_playlist.py playlist.xlsx -i
```

### 播放列表选项

| 选项                  | 简写          | 描述                           |
| --------------------- | ------------- | ------------------------------ |
| `--existing EXISTING` | `-e EXISTING` | 导入到现有播放列表的ID         |
| `--cover COVER`       | `-c COVER`    | 设置播放列表封面图片的文件路径 |

**示例：**
```bash
python import_playlist.py playlist.xlsx -e 1A2B3C4D5E6F7G8H9I0J -c cover.jpg
```

### 文件处理选项

| 选项                               | 简写            | 描述                       |
| ---------------------------------- | --------------- | -------------------------- |
| `--column-mapping MAPPING`         | `-m MAPPING`    | 列映射JSON字符串或文件路径 |
| `--skip-rows SKIP_ROWS`            | `-sr SKIP_ROWS` | 跳过文件开头的行数         |
| `--skip-empty`                     | `-se`           | 跳过空行或缺少必要信息的行 |
| `--multi-song-separator SEPARATOR` | `-ms SEPARATOR` | 多首歌曲分隔符             |

**示例：**
```bash
python import_playlist.py playlist.xlsx -m '{"歌曲":"song_name", "歌手":"artist"}' -sr 2 -se -ms "/"
```

## 交互式搜索

交互式搜索功能允许用户从多个搜索结果中选择最合适的一个，特别适用于处理有多个版本的歌曲或名称相似的歌曲。

### 启用交互式搜索

使用 `--interactive` 或 `-i` 选项启用交互式搜索：

```bash
python import_playlist.py playlist.xlsx -i
```

### 交互式搜索流程

1. 程序搜索歌曲时，如果找到多个匹配结果，会显示这些结果
2. 用户可以输入数字选择一个结果，或输入 'n' 跳过当前歌曲

**示例输出：**
```
为 'Shape of You' - Ed Sheeran 找到多个结果:
1. Shape of You - Ed Sheeran (÷ (Deluxe))
2. Shape of You - Ed Sheeran (÷)
3. Shape of You - Ed Sheeran (Shape of You)
4. Shape of You - Acoustic - Ed Sheeran (Shape of You (Acoustic))
5. Shape of You - Major Lazer Remix - Ed Sheeran (Shape of You (Major Lazer Remix))

请选择一个结果 (1-5), 或输入 'n' 跳过:
```

### 最佳实践

- 对于包含多个版本的知名歌曲，建议使用交互式搜索
- 对于大量歌曲的批量导入，可以先不使用交互式搜索，然后查看未找到的歌曲列表，再针对这些歌曲使用交互式搜索

## 预览和编辑功能

预览功能允许用户在导入前查看和编辑歌曲列表，特别适用于需要筛选或修改歌曲信息的情况。

### 启用预览

当歌曲数量超过5首时，程序默认会显示预览界面。您也可以使用 `--preview` 或 `-P` 选项强制显示预览，或使用 `--no-preview` 选项跳过预览直接导入：

```bash
python import_playlist.py playlist.xlsx --preview
```

### 预览界面操作

预览界面提供以下操作：

1. **继续导入**：确认歌曲列表并继续导入
2. **删除歌曲**：从列表中删除不需要的歌曲
3. **添加歌曲**：手动添加新歌曲
4. **编辑歌曲**：修改现有歌曲的信息
5. **测试搜索**：测试特定歌曲的搜索结果
6. **取消导入**：取消整个导入过程

### 使用场景

- **筛选歌曲**：从大型播放列表中选择部分歌曲导入
- **修正信息**：修正歌曲名或艺术家名的拼写错误
- **测试搜索**：在导入前测试特定歌曲是否能被正确找到
- **添加遗漏歌曲**：添加文件中没有但想要包含的歌曲

## 处理非标准格式文件

程序提供了多种选项来处理包含额外数据或非标准格式的文件。

### 列映射

使用 `--column-mapping` 或 `-m` 选项指定列映射，将文件中的自定义列名映射到标准列名。

**JSON字符串映射：**
```bash
python import_playlist.py playlist.xlsx -m '{"歌曲":"song_name", "歌手":"artist"}'
```

**JSON文件映射：**
创建一个 `mapping.json` 文件：
```json
{
  "歌曲": "song_name",
  "歌手": "artist",
  "专辑": "album"
}
```

然后使用文件路径：
```bash
python import_playlist.py playlist.xlsx -m mapping.json
```

### 跳过行

使用 `--skip-rows` 或 `-sr` 选项跳过文件开头的行数，适用于包含标题或说明的文件。

**示例：**
```bash
python import_playlist.py playlist.xlsx -sr 2
```

这将跳过文件的前两行，从第三行开始读取数据。

### 跳过空行

使用 `--skip-empty` 或 `-se` 选项跳过空行或缺少必要信息的行。

**示例：**
```bash
python import_playlist.py playlist.xlsx -se
```

### 多首歌曲分隔符

使用 `--multi-song-separator` 或 `-ms` 选项指定多首歌曲分隔符，用于处理一行包含多首歌曲的情况。

**示例：**
```bash
python import_playlist.py playlist.xlsx -ms "/"
```

如果文件中有一行包含 "Shape of You / Perfect"，程序会将其解析为两首歌曲。

### 复杂示例

处理一个包含标题行、自定义列名和多首歌曲的复杂文件：

```bash
python import_playlist.py complex_file.xlsx \
  -m '{"歌曲名称":"song_name", "演唱者":"artist", "多首歌曲":"song_name"}' \
  -sr 3 \
  -se \
  -ms " / " \
  -i \
  -v
```

## 导入到现有播放列表

您可以将歌曲导入到现有的 Spotify 播放列表中，而不是创建新的播放列表。

### 使用播放列表 ID

如果您知道播放列表的 ID，可以使用 `--existing` 或 `-e` 选项：

```bash
python import_playlist.py playlist.xlsx -e 1A2B3C4D5E6F7G8H9I0J
```

播放列表 ID 可以从 Spotify 播放列表链接中获取，例如：
`https://open.spotify.com/playlist/1A2B3C4D5E6F7G8H9I0J`

### 交互式选择

如果不指定播放列表 ID，程序会在导入过程中询问是否导入到现有播放列表：

```
是否导入到现有播放列表? (y/n): y
```

如果选择 "y"，程序会显示您的播放列表列表，让您选择一个：

```
找到 10 个播放列表:
  1. 我的播放列表 (25 首歌曲)
  2. 工作音乐 (42 首歌曲)
  3. 运动歌单 (18 首歌曲)
  ...

请选择要导入到的播放列表 (1-10), 或输入 'n' 创建新播放列表:
```

### 注意事项

- 导入到现有播放列表会将新歌曲添加到播放列表末尾，不会删除或替换现有歌曲
- 如果播放列表已经包含某首歌曲，程序会跳过该歌曲，不会添加重复的歌曲
- 确保您有权限修改目标播放列表（即您是播放列表的创建者或协作者）

## 设置播放列表封面

您可以为新创建的播放列表或现有播放列表设置自定义封面图片。

### 要求

- 图片必须是 JPEG 格式
- 图片大小不能超过 256KB
- 推荐尺寸为 300x300 像素或更大的正方形图片

### 使用方法

使用 `--cover` 或 `-c` 选项指定封面图片的文件路径：

```bash
python import_playlist.py playlist.xlsx -c cover.jpg
```

结合导入到现有播放列表：

```bash
python import_playlist.py playlist.xlsx -e 1A2B3C4D5E6F7G8H9I0J -c cover.jpg
```

### 注意事项

- 如果图片格式不正确或文件不存在，程序会显示错误信息
- 设置封面图片需要 `ugc-image-upload` 权限，程序会自动请求此权限
- 某些特殊播放列表（如 Spotify 生成的播放列表）可能无法设置自定义封面

## 导出播放列表

您可以将 Spotify 播放列表导出到 Excel 文件，包含歌曲详细信息。

### 基本导出

使用 `export_playlist.py` 脚本导出播放列表：

```bash
python export_playlist.py
```

如果不提供播放列表 ID，程序会显示您的播放列表列表，让您选择一个要导出的播放列表。

### 指定播放列表 ID

使用 `--id` 或 `-i` 选项指定要导出的播放列表 ID：

```bash
python export_playlist.py -i 1A2B3C4D5E6F7G8H9I0J
```

### 指定输出文件

使用 `--output` 或 `-o` 选项指定输出文件路径：

```bash
python export_playlist.py -o my_playlist_export.xlsx
```

如果不指定输出文件，程序会使用默认文件名 "playlist_名称.xlsx"。

### 导出内容

导出的 Excel 文件包含以下信息：

- 歌曲名称
- 艺术家
- 专辑
- 时长（分:秒）
- 流行度（0-100）
- 添加日期
- Spotify URI
- 外部链接

## 测试搜索功能

您可以使用 `test_search.py` 脚本测试程序的搜索功能，而不必实际创建播放列表。

### 基本搜索测试

```bash
python test_search.py "歌曲名"
```

### 指定艺术家

```bash
python test_search.py "歌曲名" --artist "艺术家名"
```

### 详细模式

使用 `--verbose` 或 `-v` 选项显示详细信息：

```bash
python test_search.py "歌曲名" --artist "艺术家名" -v
```

### 交互式搜索

使用 `--interactive` 或 `-i` 选项启用交互式搜索：

```bash
python test_search.py "歌曲名" --artist "艺术家名" -i
```

### 使用场景

- 测试特定歌曲是否能被正确找到
- 调试搜索问题
- 了解搜索算法的工作原理
- 测试不同搜索策略的效果

## 常见问题解答

### Q: 为什么有些歌曲找不到？

A: 可能的原因包括：
- 歌曲名或艺术家名拼写错误
- 歌曲在 Spotify 上的名称与您提供的不完全一致
- 该歌曲可能不在 Spotify 上架
- 地区限制可能导致某些歌曲不可用

解决方法：
- 使用交互式搜索 (`-i`) 手动选择最匹配的结果
- 修正拼写错误或尝试使用更通用的歌曲名
- 对于特殊字符或非英文歌曲，尝试使用官方拼写

### Q: 如何处理包含特殊格式的文件？

A: 使用以下选项：
- 对于自定义列名，使用 `--column-mapping` 选项
- 对于包含标题或说明的文件，使用 `--skip-rows` 选项
- 对于包含空行的文件，使用 `--skip-empty` 选项
- 对于一行包含多首歌曲的情况，使用 `--multi-song-separator` 选项

### Q: 如何提高歌曲匹配率？

A: 尝试以下方法：
- 使用交互式搜索 (`-i`)
- 确保歌曲名和艺术家名准确无误
- 对于流行歌曲的翻唱版本，指定原唱艺术家可能会有更好的结果
- 对于非英文歌曲，尝试使用官方拼写或英文译名

### Q: 为什么需要 Spotify 开发者账号？

A: Spotify API 需要开发者凭证才能访问。这是 Spotify 的安全要求，用于控制和监控 API 的使用。

### Q: 导入速度很慢，如何加快？

A: 导入速度受以下因素影响：
- 网络连接速度
- Spotify API 的限制
- 歌曲数量

优化建议：
- 确保网络连接稳定
- 对于大量歌曲，考虑分批导入
- 使用 `--no-preview` 选项跳过预览直接导入

## 高级使用技巧

### 批量处理多个文件

虽然程序目前不直接支持一次导入多个文件，但您可以使用脚本批量处理：

```bash
#!/bin/bash
for file in *.xlsx; do
  python import_playlist.py "$file" --name "${file%.xlsx} 播放列表"
done
```

### 自定义搜索策略

程序使用多种搜索策略来提高歌曲匹配率。如果您想优化特定类型的歌曲搜索，可以：

1. 对于翻唱版本，在文件中明确指定原唱艺术家
2. 对于非英文歌曲，提供官方拼写和本地化名称
3. 对于包含特殊符号的歌曲，使用标准化的名称

### 结合其他工具使用

您可以将本工具与其他音乐管理工具结合使用：

1. 使用音乐标签编辑器（如 MusicBrainz Picard）标准化您的音乐库元数据
2. 导出标准化的元数据到 Excel 或 CSV
3. 使用本工具将元数据导入到 Spotify 播放列表

### 自动化定期更新

如果您有定期更新的播放列表，可以设置自动化脚本：

```bash
#!/bin/bash
# 导出当前播放列表
python export_playlist.py -i YOUR_PLAYLIST_ID -o current_playlist.xlsx

# 合并新歌曲（需要自定义脚本）
python merge_playlists.py current_playlist.xlsx new_songs.xlsx -o updated_playlist.xlsx

# 导入更新后的播放列表
python import_playlist.py updated_playlist.xlsx -e YOUR_PLAYLIST_ID
```

### 使用环境变量

除了 `.env` 文件，您也可以使用环境变量设置 Spotify API 凭证：

```bash
export SPOTIPY_CLIENT_ID=your_client_id
export SPOTIPY_CLIENT_SECRET=your_client_secret
export SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
python import_playlist.py playlist.xlsx
```

这在服务器环境或自动化脚本中特别有用。 