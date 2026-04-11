"""Insert test history record"""
import json
from datetime import datetime
from app import create_app
from models.database import db, GenerationHistory, User

app = create_app()

with app.app_context():
    # Find current user (assuming you're logged in as admin or a specific user)
    # You can change this to your actual username
    user = User.query.first()
    
    if not user:
        print("No user found! Please create a user first.")
        exit(1)
    
    print(f"Creating test history for user: {user.username} (ID: {user.id})")
    
    # Create test history
    history = GenerationHistory(
        user_id=user.id,
        task_id='test-task-manual-001',
        title='测试历史记录 - 手动创建',
        is_pinned=False,
        product_form=json.dumps({
            'title': '测试产品',
            'targetMarket': 'US',
            'sellingPoints': '测试卖点'
        }),
        selected_image_types=json.dumps(['main', 'detail']),
        main_prompt='测试提示词',
        product_images=json.dumps([]),
        reference_images_by_type=json.dumps({}),
        competitors=json.dumps([]),
        selected_size='1024x1024',
        selected_ratio='1:1',
        selected_model='nano-banana',
        generated_image_count=2,
        success_count=2
    )
    
    db.session.add(history)
    db.session.commit()
    
    print(f"Test history created successfully! ID: {history.id}")
    print(f"Title: {history.title}")
    print(f"Created at: {history.created_at}")
    
    # Verify
    total = GenerationHistory.query.count()
    print(f"\nTotal history records: {total}")

