import os
import pandas as pd
import json
import csv
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class PlaylistReader(ABC):
    """播放列表文件读取器的抽象基类"""

    def __init__(self, file_path: str, column_mapping: Dict[str, str] = None, skip_rows: int = 0, 
                 skip_empty: bool = False, multi_song_separator: str = None, artist_column: str = None,
                 song_columns: List[str] = None, count_column: str = None):
        """
        初始化播放列表读取器
        
        Args:
            file_path: 文件路径
            column_mapping: 列映射，将文件中的列名映射到标准列名（可选）
            skip_rows: 跳过文件开头的行数（可选）
            skip_empty: 是否跳过空行或缺少必要信息的行（可选）
            multi_song_separator: 多首歌曲分隔符（可选）
            artist_column: 指定歌手列的名称（可选）
            song_columns: 指定歌曲列的名称列表（可选）
            count_column: 指定数量列的名称（可选）
        """
        self.file_path = file_path
        self.column_mapping = column_mapping or {}
        self.skip_rows = skip_rows
        self.skip_empty = skip_empty
        self.multi_song_separator = multi_song_separator
        self.artist_column = artist_column
        self.song_columns = song_columns
        self.count_column = count_column
        self.standard_columns = ['song_name', 'artist']
        self.possible_song_columns = ['song', 'song_name', 'track', 'title', 'name', '歌曲', '歌名', '曲名', '音乐', '标题']
        self.possible_artist_columns = ['artist', 'singer', 'performer', 'author', '歌手', '艺术家', '作者', '表演者']
    
    @abstractmethod
    def read_playlist(self) -> List[Dict[str, Any]]:
        """
        读取文件中的播放列表数据
        
        Returns:
            包含歌曲信息的字典列表，每个字典包含歌曲名、艺术家等信息
        
        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果文件格式不正确
        """
        pass
    
    @abstractmethod
    def get_playlist_name(self) -> str:
        """
        尝试从文件中获取播放列表名称
        
        Returns:
            播放列表名称，如果无法确定则返回文件名
        """
        pass
    
    def _get_default_playlist_name(self) -> str:
        """
        获取默认的播放列表名称（文件名，不含扩展名）
        
        Returns:
            默认的播放列表名称
        """
        return os.path.splitext(os.path.basename(self.file_path))[0]
    
    def _clean_song_data(self, songs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        清理歌曲数据（去除NaN值和空白）
        
        Args:
            songs: 原始歌曲数据
            
        Returns:
            清理后的歌曲数据
        """
        cleaned_songs = []
        for song in songs:
            # 清理数据
            for key, value in list(song.items()):  # 使用list()创建副本以避免在迭代过程中修改字典
                if pd.isna(value):
                    song[key] = ""
                elif isinstance(value, str):
                    song[key] = value.strip()
                elif value is not None:
                    # 处理非字符串类型的数据
                    try:
                        song[key] = str(value)
                    except:
                        # 如果无法转换为字符串，则设为空字符串
                        song[key] = ""
            
            # 确保song_name和artist字段存在且为字符串类型
            if 'song_name' not in song or song['song_name'] is None:
                song['song_name'] = ""
            elif not isinstance(song['song_name'], str):
                song['song_name'] = str(song['song_name'])
                
            if 'artist' not in song or song['artist'] is None:
                song['artist'] = ""
            elif not isinstance(song['artist'], str):
                song['artist'] = str(song['artist'])
            
            # 如果设置了跳过空行，则检查必要字段是否为空
            if self.skip_empty:
                if not song.get('song_name'):
                    continue
            
            cleaned_songs.append(song)
            
        return cleaned_songs
    
    def _validate_and_map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        验证数据框是否包含必要的列，并进行列映射
        
        Args:
            df: 要验证的数据框
            
        Returns:
            映射后的数据框
            
        Raises:
            ValueError: 如果缺少必要的列
        """
        # 确保数据框不为空
        if df.empty:
            raise ValueError("数据框为空，没有数据可以处理")
            
        # 处理列名，确保所有列名都是字符串类型
        df.columns = [str(col) for col in df.columns]
        
        # 如果提供了列映射，应用它
        if self.column_mapping:
            # 确保列映射中的键存在于数据框中
            valid_mapping = {k: v for k, v in self.column_mapping.items() if k in df.columns}
            if valid_mapping:
                df = df.rename(columns=valid_mapping)
        
        # 检查是否已经有标准列名
        has_song_column = 'song_name' in df.columns
        has_artist_column = 'artist' in df.columns
        
        # 如果没有标准列名，尝试智能映射
        if not has_song_column:
            for col in self.possible_song_columns:
                if col in df.columns:
                    df = df.rename(columns={col: 'song_name'})
                    has_song_column = True
                    break
        
        if not has_artist_column:
            for col in self.possible_artist_columns:
                if col in df.columns:
                    df = df.rename(columns={col: 'artist'})
                    has_artist_column = True
                    break
        
        # 如果仍然缺少必要的列，尝试从其他列推断
        if not has_song_column and len(df.columns) > 0:
            # 假设第一列是歌曲名
            df = df.rename(columns={df.columns[0]: 'song_name'})
            has_song_column = True
        
        if not has_artist_column and len(df.columns) > 1:
            # 假设第二列是艺术家
            df = df.rename(columns={df.columns[1]: 'artist'})
            has_artist_column = True
        
        # 如果仍然缺少必要的列，抛出错误
        missing_columns = []
        if not has_song_column:
            missing_columns.append('song_name')
        if not has_artist_column:
            missing_columns.append('artist')
        
        if missing_columns:
            raise ValueError(f"文件缺少必要的列: {', '.join(missing_columns)}。请使用--column-mapping选项指定列映射。")
        
        # 确保数据类型正确
        try:
            # 尝试将song_name和artist列转换为字符串类型
            df['song_name'] = df['song_name'].astype(str)
            df['artist'] = df['artist'].astype(str)
        except:
            # 如果转换失败，使用apply方法逐个处理
            df['song_name'] = df['song_name'].apply(lambda x: str(x) if x is not None else "")
            df['artist'] = df['artist'].apply(lambda x: str(x) if x is not None else "")
        
        return df
    
    def _extract_multiple_songs(self, row: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从一行数据中提取多首歌曲（处理一对多关系）
        
        Args:
            row: 一行数据
            
        Returns:
            提取的歌曲列表
        """
        songs = []
        
        # 确保获取的值是字符串类型
        song_name = str(row.get('song_name', '')) if row.get('song_name') is not None else ''
        artist = str(row.get('artist', '')) if row.get('artist') is not None else ''
        
        # 如果指定了多首歌曲分隔符，使用它
        if self.multi_song_separator and song_name and self.multi_song_separator in song_name:
            song_names = [s.strip() for s in song_name.split(self.multi_song_separator)]
            for name in song_names:
                if name:
                    songs.append({'song_name': name, 'artist': artist})
        # 否则使用默认分隔符
        elif song_name and ',' in song_name:
            song_names = [s.strip() for s in song_name.split(',')]
            for name in song_names:
                if name:
                    songs.append({'song_name': name, 'artist': artist})
        elif song_name and ';' in song_name:
            song_names = [s.strip() for s in song_name.split(';')]
            for name in song_names:
                if name:
                    songs.append({'song_name': name, 'artist': artist})
        elif song_name and '\n' in song_name:
            song_names = [s.strip() for s in song_name.split('\n')]
            for name in song_names:
                if name:
                    songs.append({'song_name': name, 'artist': artist})
        # 如果没有分隔符，就是单首歌曲
        elif song_name:
            songs.append({'song_name': song_name, 'artist': artist})
        
        # 复制其他列
        for song in songs:
            for key, value in row.items():
                if key not in ['song_name', 'artist']:
                    # 确保值是可序列化的类型
                    if value is not None:
                        try:
                            # 尝试转换为字符串
                            song[key] = str(value)
                        except:
                            # 如果无法转换，则跳过
                            pass
        
        return songs

    def _extract_songs_from_multi_columns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        从包含多个歌曲列的数据框中提取歌曲
        
        Args:
            df: 包含歌手列和多个歌曲列的数据框
            
        Returns:
            提取的歌曲列表
        """
        all_songs = []
        
        # 尝试识别歌手列
        artist_column = self.artist_column
        if artist_column is None:
            # 如果用户没有指定歌手列，尝试自动识别
            for col in df.columns:
                col_str = str(col).lower()
                if '歌手' in col_str or 'artist' in col_str or '演唱者' in col_str or '艺术家' in col_str:
                    artist_column = col
                    break
        
        # 如果仍然没有找到歌手列，尝试使用第一列作为歌手列
        if artist_column is None and len(df.columns) > 0:
            artist_column = df.columns[0]
            print(f"警告: 未找到明确的歌手列，使用第一列 '{artist_column}' 作为歌手列")
        
        # 确保歌手列存在于数据框中
        if artist_column not in df.columns:
            print(f"警告: 指定的歌手列 '{artist_column}' 不存在，尝试使用第一列作为歌手列")
            if len(df.columns) > 0:
                artist_column = df.columns[0]
            else:
                raise ValueError("数据框中没有列，无法提取歌曲")
        
        # 尝试识别歌曲列
        song_columns = self.song_columns
        if song_columns is None:
            # 如果用户没有指定歌曲列，尝试自动识别
            song_columns = []
            for col in df.columns:
                col_str = str(col).lower()
                if '歌曲' in col_str or 'song' in col_str or '曲名' in col_str or '音乐' in col_str or '标题' in col_str:
                    song_columns.append(col)
        else:
            # 确保指定的歌曲列存在于数据框中
            valid_song_columns = []
            for col in song_columns:
                if col in df.columns:
                    valid_song_columns.append(col)
                else:
                    print(f"警告: 指定的歌曲列 '{col}' 不存在，将被忽略")
            song_columns = valid_song_columns
        
        # 如果没有找到歌曲列，尝试使用除歌手列外的其他列作为歌曲列
        if not song_columns:
            for col in df.columns:
                if col != artist_column:
                    song_columns.append(col)
            print(f"警告: 未找到明确的歌曲列，使用除歌手列外的其他列作为歌曲列")
        
        # 尝试识别数量列
        count_column = self.count_column
        if count_column is None:
            # 如果用户没有指定数量列，尝试自动识别
            for col in df.columns:
                col_str = str(col).lower()
                if '数量' in col_str or 'count' in col_str or '数目' in col_str or '首数' in col_str:
                    count_column = col
                    print(f"找到数量列: '{count_column}'")
                    break
        elif count_column not in df.columns:
            print(f"警告: 指定的数量列 '{count_column}' 不存在，将被忽略")
            count_column = None
        else:
            print(f"使用指定的数量列: '{count_column}'")
        
        # 遍历每一行
        for _, row in df.iterrows():
            artist = str(row[artist_column]) if pd.notna(row[artist_column]) else ""
            
            # 如果找到了数量列，使用它来确定每行的歌曲数量
            song_count = None
            if count_column and count_column in row:
                try:
                    # 尝试将数量转换为整数
                    count_value = row[count_column]
                    if pd.notna(count_value):
                        song_count = int(float(count_value))
                        if song_count < 0:
                            song_count = None  # 忽略负数
                except (ValueError, TypeError):
                    # 如果转换失败，忽略数量列
                    pass
            
            # 遍历每个歌曲列
            valid_songs_added = 0
            for song_col in song_columns:
                # 如果已经添加了足够数量的歌曲，跳出循环
                if song_count is not None and valid_songs_added >= song_count:
                    break
                    
                song_name = row[song_col]
                
                # 跳过空值和占位符
                if pd.isna(song_name) or str(song_name).strip() == "" or str(song_name).strip() == "1":
                    continue
                
                # 将歌曲名转换为字符串
                song_name = str(song_name).strip()
                
                # 如果歌曲名包含分隔符，可能有多首歌曲
                if self.multi_song_separator and self.multi_song_separator in song_name:
                    for name in song_name.split(self.multi_song_separator):
                        name = name.strip()
                        if name and name != "1":  # 跳过占位符
                            all_songs.append({'song_name': name, 'artist': artist})
                            valid_songs_added += 1
                            # 如果已经添加了足够数量的歌曲，跳出循环
                            if song_count is not None and valid_songs_added >= song_count:
                                break
                # 检查其他常见分隔符
                elif ',' in song_name:
                    for name in song_name.split(','):
                        name = name.strip()
                        if name and name != "1":  # 跳过占位符
                            all_songs.append({'song_name': name, 'artist': artist})
                            valid_songs_added += 1
                            # 如果已经添加了足够数量的歌曲，跳出循环
                            if song_count is not None and valid_songs_added >= song_count:
                                break
                elif ';' in song_name:
                    for name in song_name.split(';'):
                        name = name.strip()
                        if name and name != "1":  # 跳过占位符
                            all_songs.append({'song_name': name, 'artist': artist})
                            valid_songs_added += 1
                            # 如果已经添加了足够数量的歌曲，跳出循环
                            if song_count is not None and valid_songs_added >= song_count:
                                break
                elif '/' in song_name:
                    for name in song_name.split('/'):
                        name = name.strip()
                        if name and name != "1":  # 跳过占位符
                            all_songs.append({'song_name': name, 'artist': artist})
                            valid_songs_added += 1
                            # 如果已经添加了足够数量的歌曲，跳出循环
                            if song_count is not None and valid_songs_added >= song_count:
                                break
                # 单首歌曲
                else:
                    if song_name != "1":  # 跳过占位符
                        all_songs.append({'song_name': song_name, 'artist': artist})
                        valid_songs_added += 1
        
        return all_songs


class ExcelReader(PlaylistReader):
    """Excel文件读取器"""
    
    def read_playlist(self) -> List[Dict[str, Any]]:
        try:
            # 读取Excel文件
            try:
                # 尝试使用默认参数读取
                df = pd.read_excel(self.file_path, skiprows=self.skip_rows)
            except Exception as e:
                # 如果失败，尝试使用更多参数
                try:
                    df = pd.read_excel(
                        self.file_path, 
                        skiprows=self.skip_rows,
                        header=None,  # 不使用标题行
                        engine='openpyxl'  # 使用openpyxl引擎
                    )
                    # 如果没有标题，使用列索引作为列名
                    df.columns = [f"Column{i}" for i in range(len(df.columns))]
                    # 假设第一列是歌曲名，第二列是艺术家
                    if len(df.columns) >= 2:
                        df = df.rename(columns={df.columns[0]: 'song_name', df.columns[1]: 'artist'})
                except Exception as inner_e:
                    raise ValueError(f"无法读取Excel文件: {str(e)}. 尝试其他方法也失败: {str(inner_e)}")
            
            # 处理空数据框
            if df.empty:
                raise ValueError("Excel文件为空或没有有效数据")
                
            # 处理NaN值
            df = df.fillna("")
            
            # 检测是否是多列歌曲表格
            is_multi_column_format = False
            song_column_count = 0
            
            # 检查列名中是否包含多个歌曲列
            for col in df.columns:
                col_str = str(col).lower()
                if '歌曲' in col_str or 'song' in col_str or '曲名' in col_str:
                    song_column_count += 1
            
            # 如果有多个歌曲列，认为是多列格式
            if song_column_count > 1:
                is_multi_column_format = True
                print(f"检测到多列歌曲格式，共有 {song_column_count} 个歌曲列")
            
            # 根据格式选择不同的处理方法
            if is_multi_column_format:
                # 使用多列处理方法
                all_songs = self._extract_songs_from_multi_columns(df)
            else:
                # 使用标准处理方法
                # 验证并映射列
                df = self._validate_and_map_columns(df)
                
                # 转换为字典列表
                rows = df.to_dict('records')
                
                # 提取歌曲
                all_songs = []
                for row in rows:
                    try:
                        songs = self._extract_multiple_songs(row)
                        all_songs.extend(songs)
                    except Exception as e:
                        # 如果处理某一行出错，记录错误并继续
                        print(f"警告: 处理行 {row} 时出错: {str(e)}. 跳过此行。")
                        continue
            
            # 清理数据
            all_songs = self._clean_song_data(all_songs)
            
            if not all_songs:
                raise ValueError("Excel文件中没有找到有效的歌曲")
            
            return all_songs
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取Excel文件时出错: {str(e)}")
    
    def get_playlist_name(self) -> str:
        try:
            # 尝试读取Excel文件的第一个工作表名称作为播放列表名称
            xl = pd.ExcelFile(self.file_path)
            sheet_name = xl.sheet_names[0]
            
            # 如果工作表名称不是默认的（如Sheet1），则使用它
            if sheet_name.lower() not in ['sheet1', 'sheet2', 'sheet3', 'sheet']:
                return sheet_name
            
            # 如果无法从内容确定，则使用文件名
            return self._get_default_playlist_name()
            
        except Exception:
            # 出错时使用文件名
            return self._get_default_playlist_name()


class CSVReader(PlaylistReader):
    """CSV文件读取器"""
    
    def read_playlist(self) -> List[Dict[str, Any]]:
        try:
            # 读取CSV文件
            df = pd.read_csv(self.file_path, skiprows=self.skip_rows)
            
            # 处理空数据框
            if df.empty:
                raise ValueError("CSV文件为空或没有有效数据")
                
            # 处理NaN值
            df = df.fillna("")
            
            # 检测是否是多列歌曲表格
            is_multi_column_format = False
            song_column_count = 0
            
            # 检查列名中是否包含多个歌曲列
            for col in df.columns:
                col_str = str(col).lower()
                if '歌曲' in col_str or 'song' in col_str or '曲名' in col_str:
                    song_column_count += 1
            
            # 如果有多个歌曲列，认为是多列格式
            if song_column_count > 1:
                is_multi_column_format = True
                print(f"检测到多列歌曲格式，共有 {song_column_count} 个歌曲列")
            
            # 根据格式选择不同的处理方法
            if is_multi_column_format:
                # 使用多列处理方法
                all_songs = self._extract_songs_from_multi_columns(df)
            else:
                # 使用标准处理方法
                # 验证并映射列
                df = self._validate_and_map_columns(df)
                
                # 转换为字典列表
                rows = df.to_dict('records')
                
                # 提取歌曲
                all_songs = []
                for row in rows:
                    try:
                        songs = self._extract_multiple_songs(row)
                        all_songs.extend(songs)
                    except Exception as e:
                        # 如果处理某一行出错，记录错误并继续
                        print(f"警告: 处理行 {row} 时出错: {str(e)}. 跳过此行。")
                        continue
            
            # 清理数据
            all_songs = self._clean_song_data(all_songs)
            
            if not all_songs:
                raise ValueError("CSV文件中没有找到有效的歌曲")
            
            return all_songs
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取CSV文件时出错: {str(e)}")
    
    def get_playlist_name(self) -> str:
        # CSV文件没有内置的名称，使用文件名
        return self._get_default_playlist_name()


class JSONReader(PlaylistReader):
    """JSON文件读取器"""
    
    def read_playlist(self) -> List[Dict[str, Any]]:
        try:
            # 读取JSON文件
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理不同的JSON格式
            songs = []
            
            # 如果是列表格式
            if isinstance(data, list):
                # 跳过指定的行数
                if self.skip_rows > 0:
                    data = data[self.skip_rows:]
                
                # 检查列表中的每个项目是否是字典
                for item in data:
                    if isinstance(item, dict):
                        # 应用列映射
                        mapped_item = {}
                        for key, value in item.items():
                            mapped_key = self.column_mapping.get(key, key)
                            mapped_item[mapped_key] = value
                        
                        # 提取歌曲
                        extracted_songs = self._extract_multiple_songs(mapped_item)
                        songs.extend(extracted_songs)
            
            # 如果是对象格式
            elif isinstance(data, dict):
                # 检查是否有songs字段
                if 'songs' in data and isinstance(data['songs'], list):
                    # 跳过指定的行数
                    songs_data = data['songs']
                    if self.skip_rows > 0:
                        songs_data = songs_data[self.skip_rows:]
                    
                    # 处理每首歌曲
                    for item in songs_data:
                        if isinstance(item, dict):
                            # 应用列映射
                            mapped_item = {}
                            for key, value in item.items():
                                mapped_key = self.column_mapping.get(key, key)
                                mapped_item[mapped_key] = value
                            
                            # 提取歌曲
                            extracted_songs = self._extract_multiple_songs(mapped_item)
                            songs.extend(extracted_songs)
                
                # 如果没有songs字段，尝试直接使用对象
                else:
                    # 应用列映射
                    mapped_item = {}
                    for key, value in data.items():
                        mapped_key = self.column_mapping.get(key, key)
                        mapped_item[mapped_key] = value
                    
                    # 提取歌曲
                    extracted_songs = self._extract_multiple_songs(mapped_item)
                    songs.extend(extracted_songs)
            
            # 清理数据
            songs = self._clean_song_data(songs)
            
            if not songs:
                raise ValueError("JSON文件中没有找到有效的歌曲")
            
            return songs
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {self.file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"无效的JSON格式: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取JSON文件时出错: {str(e)}")
    
    def get_playlist_name(self) -> str:
        try:
            # 尝试从JSON文件中读取播放列表名称
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 如果是对象格式且有name字段
            if isinstance(data, dict) and 'name' in data:
                return data['name']
            
            # 如果无法从内容确定，则使用文件名
            return self._get_default_playlist_name()
            
        except Exception:
            # 出错时使用文件名
            return self._get_default_playlist_name()


class TextReader(PlaylistReader):
    """文本文件读取器"""
    
    def read_playlist(self) -> List[Dict[str, Any]]:
        try:
            # 读取文本文件
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 跳过指定的行数
            if self.skip_rows > 0:
                lines = lines[self.skip_rows:]
            
            # 提取歌曲
            songs = []
            for line in lines:
                line = line.strip()
                
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                # 尝试解析"歌曲名 - 艺术家"格式
                if ' - ' in line:
                    parts = line.split(' - ', 1)
                    song_name = parts[0].strip()
                    artist = parts[1].strip() if len(parts) > 1 else ""
                # 尝试解析"艺术家 - 歌曲名"格式
                elif ' – ' in line:  # 注意这是不同的破折号
                    parts = line.split(' – ', 1)
                    song_name = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                    artist = parts[0].strip() if len(parts) > 1 else ""
                # 如果没有分隔符，假设整行是歌曲名
                else:
                    song_name = line
                    artist = ""
                
                # 如果指定了多首歌曲分隔符，处理多首歌曲
                if self.multi_song_separator and self.multi_song_separator in song_name:
                    song_names = [s.strip() for s in song_name.split(self.multi_song_separator)]
                    for name in song_names:
                        if name:
                            songs.append({
                                'song_name': name.strip(),
                                'artist': artist.strip()
                            })
                else:
                    songs.append({
                        'song_name': song_name.strip(),
                        'artist': artist.strip()
                    })
            
            # 清理数据
            songs = self._clean_song_data(songs)
            
            if not songs:
                raise ValueError("文本文件中没有找到有效的歌曲")
            
            return songs
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取文本文件时出错: {str(e)}")
    
    def get_playlist_name(self) -> str:
        try:
            # 尝试读取文件的第一行作为播放列表名称（如果以#开头）
            with open(self.file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('# '):
                    return first_line[2:].strip()
            
            # 如果无法从内容确定，则使用文件名
            return self._get_default_playlist_name()
            
        except Exception:
            # 出错时使用文件名
            return self._get_default_playlist_name()


def get_reader(file_path: str, column_mapping: Dict[str, str] = None, skip_rows: int = 0, 
               skip_empty: bool = False, multi_song_separator: str = None, artist_column: str = None,
               song_columns: List[str] = None, count_column: str = None) -> PlaylistReader:
    """
    根据文件扩展名获取合适的读取器
    
    Args:
        file_path: 文件路径
        column_mapping: 列映射，将文件中的列名映射到标准列名（可选）
        skip_rows: 跳过文件开头的行数（可选）
        skip_empty: 是否跳过空行或缺少必要信息的行（可选）
        multi_song_separator: 多首歌曲分隔符（可选）
        artist_column: 指定歌手列的名称（可选）
        song_columns: 指定歌曲列的名称列表（可选）
        count_column: 指定数量列的名称（可选）
        
    Returns:
        适合该文件类型的读取器实例
        
    Raises:
        ValueError: 如果文件类型不受支持
    """
    _, ext = os.path.splitext(file_path.lower())
    
    reader_args = {
        'file_path': file_path,
        'column_mapping': column_mapping,
        'skip_rows': skip_rows,
        'skip_empty': skip_empty,
        'multi_song_separator': multi_song_separator,
        'artist_column': artist_column,
        'song_columns': song_columns,
        'count_column': count_column
    }
    
    if ext in ['.xlsx', '.xls', '.xlsm']:
        return ExcelReader(**reader_args)
    elif ext == '.csv':
        return CSVReader(**reader_args)
    elif ext == '.json':
        return JSONReader(**reader_args)
    elif ext in ['.txt', '.text']:
        return TextReader(**reader_args)
    else:
        raise ValueError(f"不支持的文件类型: {ext}") 