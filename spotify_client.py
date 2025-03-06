import os
import time
from typing import List, Dict, Any, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


class SpotifyClient:
    """用于与Spotify API交互的客户端类"""
    
    def __init__(self):
        """初始化Spotify客户端并进行认证"""
        # 加载环境变量
        load_dotenv()
        
        # 获取Spotify API凭证
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            raise ValueError("缺少Spotify API凭证。请在.env文件中设置SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET和SPOTIFY_REDIRECT_URI")
        
        # 设置权限范围
        scope = "playlist-modify-public playlist-modify-private"
        
        # 创建Spotify客户端
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        ))
        
        # 获取当前用户信息
        self.user_id = self.sp.current_user()['id']
    
    def create_playlist(self, name: str, description: str = "") -> str:
        """
        创建新的Spotify播放列表
        
        Args:
            name: 播放列表名称
            description: 播放列表描述
            
        Returns:
            新创建的播放列表ID
        """
        playlist = self.sp.user_playlist_create(
            user=self.user_id,
            name=name,
            public=True,
            description=description
        )
        return playlist['id']
    
    def search_track(self, song_name: str, artist: str = "") -> Optional[str]:
        """
        在Spotify上搜索歌曲
        
        Args:
            song_name: 歌曲名称
            artist: 艺术家名称（可选）
            
        Returns:
            歌曲ID，如果未找到则返回None
        """
        # 构建搜索查询
        query = f"track:{song_name}"
        if artist:
            query += f" artist:{artist}"
        
        # 搜索歌曲
        results = self.sp.search(q=query, type='track', limit=1)
        
        # 检查是否找到结果
        if results['tracks']['items']:
            return results['tracks']['items'][0]['id']
        
        # 如果没有找到，尝试只用歌曲名搜索
        if artist:
            results = self.sp.search(q=f"track:{song_name}", type='track', limit=1)
            if results['tracks']['items']:
                return results['tracks']['items'][0]['id']
        
        return None
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        """
        将歌曲添加到播放列表
        
        Args:
            playlist_id: 播放列表ID
            track_ids: 歌曲ID列表
            
        Returns:
            是否成功添加
        """
        # Spotify API限制一次最多添加100首歌曲
        chunk_size = 100
        
        for i in range(0, len(track_ids), chunk_size):
            chunk = track_ids[i:i + chunk_size]
            self.sp.playlist_add_items(playlist_id, chunk)
            
            # 添加短暂延迟以避免API限制
            if i + chunk_size < len(track_ids):
                time.sleep(1)
        
        return True 