import pandas as pd
from typing import List, Dict, Any


class ExcelReader:
    """用于从Excel文件中读取播放列表数据的类"""

    def __init__(self, file_path: str):
        """
        初始化Excel读取器
        
        Args:
            file_path: Excel文件的路径
        """
        self.file_path = file_path
        
    def read_playlist(self) -> List[Dict[str, Any]]:
        """
        读取Excel文件中的播放列表数据
        
        Returns:
            包含歌曲信息的字典列表，每个字典包含歌曲名、艺术家等信息
        
        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果文件格式不正确
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(self.file_path)
            
            # 检查必要的列是否存在
            required_columns = ['song_name', 'artist']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Excel文件缺少必要的列: {', '.join(missing_columns)}")
            
            # 转换为字典列表
            songs = df.to_dict('records')
            
            # 清理数据（去除NaN值和空白）
            for song in songs:
                for key, value in song.items():
                    if pd.isna(value):
                        song[key] = ""
                    elif isinstance(value, str):
                        song[key] = value.strip()
            
            return songs
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取Excel文件时出错: {str(e)}")
    
    def get_playlist_name(self) -> str:
        """
        尝试从Excel文件中获取播放列表名称
        
        Returns:
            播放列表名称，如果无法确定则返回文件名
        """
        try:
            # 尝试读取文件的第一行第一列作为播放列表名称
            df = pd.read_excel(self.file_path, nrows=1)
            if not df.empty and len(df.columns) > 0:
                playlist_name = df.iloc[0, 0]
                if isinstance(playlist_name, str) and playlist_name.strip():
                    return playlist_name.strip()
            
            # 如果无法从内容确定，则使用文件名（不含扩展名）
            import os
            return os.path.splitext(os.path.basename(self.file_path))[0]
            
        except Exception:
            # 出错时使用文件名
            import os
            return os.path.splitext(os.path.basename(self.file_path))[0] 