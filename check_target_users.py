#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from db.session import get_db
from db.models import Message, User

def check_target_users():
    db = next(get_db())
    
    try:
        # 查看LG Gram商品的消息，特别关注target_users字段
        lg_gram_messages = db.query(Message).filter(Message.item_id == 32).limit(10).all()
        print(f'LG Gram商品的消息示例:')
        for msg in lg_gram_messages:
            sender = db.query(User).filter(User.id == msg.user_id).first()
            sender_name = sender.username if sender else f'用户{msg.user_id}'
            print(f'  - ID: {msg.id}, 发送者: {sender_name}({msg.user_id}), target_users: {msg.target_users}, 内容: {str(msg.content)[:30]}...')
            
        # 查看target_users字段的唯一值
        unique_target_users = db.query(Message.target_users).filter(
            Message.item_id == 32,
            Message.target_users.isnot(None)
        ).distinct().all()
        
        print(f'\\nLG Gram商品的target_users唯一值:')
        for row in unique_target_users:
            print(f'  - {row[0]}')
            
        # 查看用户1与刘童的消息（通过target_users字段）
        print(f'\\n用户1与刘童的消息（通过target_users字段）:')
        user1_liutong_messages = db.query(Message).filter(
            Message.item_id == 32,
            Message.target_users == '11'  # 刘童的用户ID
        ).order_by(Message.created_at.desc()).limit(5).all()
        
        for msg in user1_liutong_messages:
            sender = db.query(User).filter(User.id == msg.user_id).first()
            sender_name = sender.username if sender else f'用户{msg.user_id}'
            print(f'  - ID: {msg.id}, 发送者: {sender_name}({msg.user_id}), target_users: {msg.target_users}, 内容: {str(msg.content)[:30]}...')
            
        # 查看用户1与testadmin的消息（通过target_users字段）
        print(f'\\n用户1与testadmin的消息（通过target_users字段）:')
        user1_testadmin_messages = db.query(Message).filter(
            Message.item_id == 32,
            Message.target_users == '28'  # testadmin的用户ID
        ).order_by(Message.created_at.desc()).limit(5).all()
        
        for msg in user1_testadmin_messages:
            sender = db.query(User).filter(User.id == msg.user_id).first()
            sender_name = sender.username if sender else f'用户{msg.user_id}'
            print(f'  - ID: {msg.id}, 发送者: {sender_name}({msg.user_id}), target_users: {msg.target_users}, 内容: {str(msg.content)[:30]}...')
        
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    check_target_users()
