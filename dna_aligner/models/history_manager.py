"""
历史记录管理器
使用SQLite数据库存储比对历史记录
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from .alignment_result import AlignmentResult


class HistoryManager:
    """历史记录管理器"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化历史记录管理器

        Args:
            db_path: 数据库文件路径，默认为程序目录下的history.db
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "history.db")

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alignment_history (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    ref_original TEXT NOT NULL,
                    query_original TEXT NOT NULL,
                    ref_alignment TEXT NOT NULL,
                    query_alignment TEXT NOT NULL,
                    match_mark TEXT NOT NULL,
                    start_pos INTEGER NOT NULL,
                    end_pos INTEGER NOT NULL,
                    similarity REAL NOT NULL,
                    score INTEGER NOT NULL,
                    device_info TEXT,
                    batch_index INTEGER,
                    batch_total INTEGER,
                    tags TEXT,
                    notes TEXT
                )
            ''')

            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON alignment_history(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_similarity
                ON alignment_history(similarity)
            ''')

            conn.commit()

    def save(self, result: AlignmentResult, tags: str = "", notes: str = "") -> str:
        """
        保存比对结果到历史记录

        Args:
            result: 比对结果
            tags: 标签（逗号分隔）
            notes: 备注

        Returns:
            str: 记录ID
        """
        if result.alignment_id is None:
            result.alignment_id = str(uuid.uuid4())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alignment_history
                (id, timestamp, ref_original, query_original, ref_alignment,
                 query_alignment, match_mark, start_pos, end_pos, similarity,
                 score, device_info, batch_index, batch_total, tags, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.alignment_id,
                result.timestamp.isoformat(),
                result.ref_original,
                result.query_original,
                result.ref_alignment,
                result.query_alignment,
                result.match_mark,
                result.start_pos,
                result.end_pos,
                result.similarity,
                result.score,
                result.device_info,
                result.batch_index,
                result.batch_total,
                tags,
                notes
            ))
            conn.commit()

        return result.alignment_id

    def load(self, record_id: str) -> Optional[AlignmentResult]:
        """
        根据ID加载历史记录

        Args:
            record_id: 记录ID

        Returns:
            Optional[AlignmentResult]: 比对结果，不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, timestamp, ref_original, query_original, ref_alignment,
                       query_alignment, match_mark, start_pos, end_pos, similarity,
                       score, device_info, batch_index, batch_total
                FROM alignment_history
                WHERE id = ?
            ''', (record_id,))

            row = cursor.fetchone()
            if row is None:
                return None

            return self._row_to_result(row)

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = 'timestamp',
        order_desc: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取所有历史记录（摘要信息）

        Args:
            limit: 返回记录数限制
            offset: 偏移量
            order_by: 排序字段（timestamp, similarity, score）
            order_desc: 是否降序

        Returns:
            List[Dict]: 历史记录摘要列表
        """
        # 白名单校验，防止SQL注入
        ORDER_CLAUSES = {
            'timestamp': 'timestamp',
            'similarity': 'similarity',
            'score': 'score'
        }
        order_clause = ORDER_CLAUSES.get(order_by, 'timestamp')
        order_dir = 'DESC' if order_desc else 'ASC'

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT id, timestamp, ref_original, query_original,
                       similarity, score, device_info, tags, notes
                FROM alignment_history
                ORDER BY {order_clause} {order_dir}
                LIMIT ? OFFSET ?
            ''', (limit, offset))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'ref_preview': row[2][:20] + '...' if len(row[2]) > 20 else row[2],
                    'query_preview': row[3][:20] + '...' if len(row[3]) > 20 else row[3],
                    'ref_original': row[2],
                    'query_original': row[3],
                    'similarity': row[4],
                    'score': row[5],
                    'device_info': row[6],
                    'tags': row[7] or '',
                    'notes': row[8] or ''
                })

            return results

    def search(
        self,
        query: str = "",
        min_similarity: float = 0,
        max_similarity: float = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        搜索历史记录

        Args:
            query: 搜索关键词（匹配序列或备注）
            min_similarity: 最小相似度
            max_similarity: 最大相似度
            start_date: 开始日期（ISO格式）
            end_date: 结束日期（ISO格式）
            limit: 返回记录数限制

        Returns:
            List[Dict]: 匹配的历史记录列表
        """
        conditions = []
        params = []

        if query:
            conditions.append(
                "(ref_original LIKE ? OR query_original LIKE ? OR notes LIKE ?)"
            )
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])

        if min_similarity > 0:
            conditions.append("similarity >= ?")
            params.append(min_similarity)

        if max_similarity < 100:
            conditions.append("similarity <= ?")
            params.append(max_similarity)

        if start_date:
            conditions.append("timestamp >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("timestamp <= ?")
            params.append(end_date)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT id, timestamp, ref_original, query_original,
                       similarity, score, device_info, tags, notes
                FROM alignment_history
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            ''', params + [limit])

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'ref_preview': row[2][:20] + '...' if len(row[2]) > 20 else row[2],
                    'query_preview': row[3][:20] + '...' if len(row[3]) > 20 else row[3],
                    'ref_original': row[2],
                    'query_original': row[3],
                    'similarity': row[4],
                    'score': row[5],
                    'device_info': row[6],
                    'tags': row[7] or '',
                    'notes': row[8] or ''
                })

            return results

    def delete(self, record_id: str) -> bool:
        """
        删除历史记录

        Args:
            record_id: 记录ID

        Returns:
            bool: 是否删除成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM alignment_history WHERE id = ?",
                (record_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self) -> int:
        """
        清空所有历史记录

        Returns:
            int: 删除的记录数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alignment_history")
            conn.commit()
            return cursor.rowcount

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取历史记录统计信息

        Returns:
            Dict: 统计信息
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 总记录数
            cursor.execute("SELECT COUNT(*) FROM alignment_history")
            total_count = cursor.fetchone()[0]

            # 平均相似度
            cursor.execute("SELECT AVG(similarity) FROM alignment_history")
            avg_similarity = cursor.fetchone()[0] or 0

            # 最高相似度
            cursor.execute("SELECT MAX(similarity) FROM alignment_history")
            max_similarity = cursor.fetchone()[0] or 0

            # 最低相似度
            cursor.execute("SELECT MIN(similarity) FROM alignment_history")
            min_similarity = cursor.fetchone()[0] or 0

            # 最近记录
            cursor.execute('''
                SELECT timestamp FROM alignment_history
                ORDER BY timestamp DESC LIMIT 1
            ''')
            last_record = cursor.fetchone()
            last_timestamp = last_record[0] if last_record else None

            return {
                'total_count': total_count,
                'avg_similarity': round(avg_similarity, 1),
                'max_similarity': max_similarity,
                'min_similarity': min_similarity,
                'last_timestamp': last_timestamp
            }

    def _row_to_result(self, row: tuple) -> AlignmentResult:
        """将数据库行转换为AlignmentResult对象"""
        return AlignmentResult(
            alignment_id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            ref_original=row[2],
            query_original=row[3],
            ref_alignment=row[4],
            query_alignment=row[5],
            match_mark=row[6],
            start_pos=row[7],
            end_pos=row[8],
            similarity=row[9],
            score=row[10],
            device_info=row[11] or '',
            batch_index=row[12],
            batch_total=row[13]
        )
