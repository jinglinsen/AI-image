"""
数据库迁移脚本
为现有表添加 user_id 列
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.database import db
import sqlite3

def migrate_database():
    """迁移数据库，添加缺失的列"""
    app = create_app()
    
    with app.app_context():
        db_path = 'instance/aigc_assistant.db'
        
        if not os.path.exists(db_path):
            print("数据库不存在，请先运行 init_database.py")
            return
        
        print("开始数据库迁移...")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取默认管理员ID
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_result = cursor.fetchone()
        if admin_result:
            admin_id = admin_result[0]
        else:
            print("[错误] 找不到管理员账号，请先运行 init_database.py")
            conn.close()
            return
        
        print(f"使用管理员ID: {admin_id} 作为默认用户")
        
        # 检查并添加 user_id 列到各个表
        tables_to_migrate = [
            ('generation_tasks', 'generation_tasks'),
            ('generated_images', 'generated_images'),
            ('generation_history', 'generation_history'),
            ('api_usage', 'api_usage')
        ]
        
        for table_name, display_name in tables_to_migrate:
            try:
                # 检查列是否存在
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'user_id' not in columns:
                    print(f"  为 {display_name} 添加 user_id 列...")
                    cursor.execute(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN user_id INTEGER
                    """)
                    
                    # 将现有记录的 user_id 设置为管理员ID
                    cursor.execute(f"""
                        UPDATE {table_name}
                        SET user_id = ?
                        WHERE user_id IS NULL
                    """, (admin_id,))
                    
                    print(f"  [OK] {display_name} 迁移完成")
                else:
                    print(f"  [跳过] {display_name} 已有 user_id 列")
            
            except sqlite3.Error as e:
                print(f"  [错误] {display_name} 迁移失败: {e}")
        
        # 为 generation_history 添加其他新列
        try:
            cursor.execute("PRAGMA table_info(generation_history)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'title' not in columns:
                print("  为 generation_history 添加 title 列...")
                cursor.execute("""
                    ALTER TABLE generation_history
                    ADD COLUMN title VARCHAR(200)
                """)
                print("  [OK] title 列添加完成")
            
            if 'is_pinned' not in columns:
                print("  为 generation_history 添加 is_pinned 列...")
                cursor.execute("""
                    ALTER TABLE generation_history
                    ADD COLUMN is_pinned BOOLEAN DEFAULT 0
                """)
                print("  [OK] is_pinned 列添加完成")
        
        except sqlite3.Error as e:
            print(f"  [错误] generation_history 扩展列迁移失败: {e}")
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("\n数据库迁移完成！")
        print("所有现有数据已关联到管理员账号")

if __name__ == '__main__':
    migrate_database()

