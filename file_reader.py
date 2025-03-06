import os
import pandas as pd
import json
import csv
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class PlaylistReader(ABC):
    """播放列表文件读取器的抽象基类"""

    def __init__(self, file_path: str):
        """
        初始化播放列表读取器
        
        Args:
            file_path: 文件路径
        """
        self.file_path = file_path
    
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
        for song in songs:
            for key, value in song.items():
                if pd.isna(value):
                    song[key] = ""
                elif isinstance(value, str):
                    song[key] = value.strip()
        return songs
    
    def _validate_required_columns(self, df: pd.DataFrame) -> None:
        """
        验证数据框是否包含必要的列
        
        Args:
            df: 要验证的数据框
            
        Raises:
            ValueError: 如果缺少必要的列
        """
        required_columns = ['song_name', 'artist']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"文件缺少必要的列: {', '.join(missing_columns)}")


class ExcelReader(PlaylistReader):
    """Excel文件读取器"""
    
    def read_playlist(self) -> List[Dict[str, Any]]:
        try:
            # 读取Excel文件
            df = pd.read_excel(self.file_path)
            
            # 验证必要的列
            self._validate_required_columns(df)
            
            # 转换为字典列表并清理数据
            songs = df.to_dict('records')
            return self._clean_song_data(songs)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取Excel文件时出错: {str(e)}")
    
    def get_playlist_name(self) -> str:
        try:
            # 尝试读取文件的第一行第一列作为播放列表名称
            df = pd.read_excel(self.file_path, nrows=1)
            if not df.empty and len(df.columns) > 0:
                playlist_name = df.iloc[0, 0]
                if isinstance(playlist_name, str) and playlist_name.strip():
                    return playlist_name.strip()
            
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
            df = pd.read_csv(self.file_path)
            
            # 验证必要的列
            self._validate_required_columns(df)
            
            # 转换为字典列表并清理数据
            songs = df.to_dict('records')
            return self._clean_song_data(songs)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取CSV文件时出错: {str(e)}")
    
    def get_playlist_name(self) -> str:
        try:
            # 尝试读取文件的第一行作为播放列表名称
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                first_row = next(reader, None)
                if first_row and len(first_row) > 0 and first_row[0].strip():
                    return first_row[0].strip()
            
            # 如果无法从内容确定，则使用文件名
            return self._get_default_playlist_name()
            
        except Exception:
            # 出错时使用文件名
            return self._get_default_playlist_name()


class JSONReader(PlaylistReader):
    """JSON文件读取器"""
    
    def read_playlist(self) -> List[Dict[str, Any]]:
        try:
            # 读取JSON文件
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理不同的JSON结构
            songs = []
            if isinstance(data, list):
                # 如果是歌曲列表
                songs = data
            elif isinstance(data, dict):
                # 如果是包含歌曲列表的字典
                if 'songs' in data and isinstance(data['songs'], list):
                    songs = data['songs']
                elif 'tracks' in data and isinstance(data['tracks'], list):
                    songs = data['tracks']
                elif 'playlist' in data and isinstance(data['playlist'], list):
                    songs = data['playlist']
            
            # 验证歌曲数据
            if not songs:
                raise ValueError("JSON文件中没有找到有效的歌曲列表")
            
            # 确保每首歌都有必要的字段
            for song in songs:
                if 'song_name' not in song and 'title' in song:
                    song['song_name'] = song['title']
                if 'song_name' not in song and 'name' in song:
                    song['song_name'] = song['name']
                if 'artist' not in song and 'artist_name' in song:
                    song['artist'] = song['artist_name']
                if 'artist' not in song and 'performer' in song:
                    song['artist'] = song['performer']
            
            # 验证必要的列
            missing_song_name = any('song_name' not in song for song in songs)
            missing_artist = any('artist' not in song for song in songs)
            
            if missing_song_name or missing_artist:
                missing = []
                if missing_song_name:
                    missing.append('song_name')
                if missing_artist:
                    missing.append('artist')
                raise ValueError(f"JSON文件中的歌曲缺少必要的字段: {', '.join(missing)}")
            
            return self._clean_song_data(songs)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {self.file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"无效的JSON格式: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取JSON文件时出错: {str(e)}")
    
    def get_playlist_name(self) -> str:
        try:
            # 尝试从JSON文件中获取播放列表名称
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                # 尝试从字典中获取播放列表名称
                for key in ['name', 'playlist_name', 'title']:
                    if key in data and isinstance(data[key], str) and data[key].strip():
                        return data[key].strip()
            
            # 如果无法从内容确定，则使用文件名
            return self._get_default_playlist_name()
            
        except Exception:
            # 出错时使用文件名
            return self._get_default_playlist_name()


class TextReader(PlaylistReader):
    """文本文件读取器（每行一首歌）"""
    
    def read_playlist(self) -> List[Dict[str, Any]]:
        try:
            # 读取文本文件
            songs = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue  # 跳过空行和注释
                    
                    # 尝试解析歌曲和艺术家
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        song_name, artist = parts
                    else:
                        song_name, artist = line, ""
                    
                    songs.append({
                        'song_name': song_name.strip(),
                        'artist': artist.strip()
                    })
            
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


def get_reader(file_path: str) -> PlaylistReader:
    """
    根据文件扩展名获取合适的读取器
    
    Args:
        file_path: 文件路径
        
    Returns:
        适合该文件类型的读取器实例
        
    Raises:
        ValueError: 如果文件类型不受支持
    """
    _, ext = os.path.splitext(file_path.lower())
    
    if ext in ['.xlsx', '.xls', '.xlsm']:
        return ExcelReader(file_path)
    elif ext == '.csv':
        return CSVReader(file_path)
    elif ext == '.json':
        return JSONReader(file_path)
    elif ext in ['.txt', '.text']:
        return TextReader(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {ext}") 