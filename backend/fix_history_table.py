"""Fix generation_history table - remove session_id column"""
import sys
from sqlalchemy import text, inspect
from app import create_app
from models.database import db

def fix_history_table():
    app = create_app()
    with app.app_context():
        print("Fixing generation_history table...")
        
        inspector = inspect(db.engine)
        
        # Check if session_id column exists
        columns = [col['name'] for col in inspector.get_columns('generation_history')]
        print(f"Current columns: {columns}")
        
        if 'session_id' in columns:
            print("\nRemoving session_id column...")
            try:
                # SQLite doesn't support DROP COLUMN directly
                # We need to recreate the table
                
                # 1. Create new table without session_id
                db.session.execute(text("""
                    CREATE TABLE generation_history_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        task_id VARCHAR(36) NOT NULL,
                        title VARCHAR(200),
                        is_pinned BOOLEAN DEFAULT 0,
                        product_form VARCHAR(100),
                        selected_image_types TEXT,
                        main_prompt TEXT,
                        product_images TEXT,
                        reference_images_by_type TEXT,
                        competitors TEXT,
                        selected_size VARCHAR(20),
                        selected_ratio VARCHAR(10),
                        selected_model VARCHAR(50),
                        generated_image_count INTEGER DEFAULT 0,
                        success_count INTEGER DEFAULT 0,
                        generation_time FLOAT,
                        user_rating INTEGER,
                        user_notes TEXT,
                        is_favorite BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (task_id) REFERENCES generation_tasks(task_id)
                    )
                """))
                
                # 2. Copy data from old table (if any)
                db.session.execute(text("""
                    INSERT INTO generation_history_new 
                    SELECT id, user_id, task_id, title, is_pinned, product_form, 
                           selected_image_types, main_prompt, product_images,
                           reference_images_by_type, competitors, selected_size,
                           selected_ratio, selected_model, generated_image_count,
                           success_count, generation_time, user_rating, user_notes,
                           is_favorite, created_at, updated_at
                    FROM generation_history
                """))
                
                # 3. Drop old table
                db.session.execute(text("DROP TABLE generation_history"))
                
                # 4. Rename new table
                db.session.execute(text("ALTER TABLE generation_history_new RENAME TO generation_history"))
                
                db.session.commit()
                print("SUCCESS: session_id column removed!")
                
            except Exception as e:
                db.session.rollback()
                print(f"ERROR: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("session_id column does not exist, no fix needed.")
        
        # Verify
        columns = [col['name'] for col in inspector.get_columns('generation_history')]
        print(f"\nFinal columns: {columns}")

if __name__ == '__main__':
    fix_history_table()

