#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from db.session import get_db
from db.models import Message, Item, User

def check_lg_gram():
    db = next(get_db())
    
    try:
        # 查找LG Gram笔记本电脑商品
        lg_gram_item = db.query(Item).filter(Item.title.like('%LG Gram%')).first()
        if lg_gram_item:
            print(f'LG Gram商品ID: {lg_gram_item.id}, 标题: {str(lg_gram_item.title)}, 所有者: {lg_gram_item.owner_id}')
            
            # 查找关于这个商品的所有消息
            messages = db.query(Message).filter(Message.item_id == lg_gram_item.id).order_by(Message.created_at.desc()).all()
            print(f'\\n关于LG Gram商品的消息数: {len(messages)}')
            
            for msg in messages[:10]:  # 只显示前10条
                sender = db.query(User).filter(User.id == msg.user_id).first()
                sender_name = sender.username if sender else f'用户{msg.user_id}'
                print(f'  - 消息ID: {msg.id}, 发送者: {sender_name}({msg.user_id}), 内容: {str(msg.content)[:50]}..., 时间: {msg.created_at}')
                
            # 查找用户1与刘童关于这个商品的消息
            print(f'\\n用户1与刘童关于LG Gram商品的消息:')
            user1_liutong_messages = db.query(Message).filter(
                Message.item_id == lg_gram_item.id,
                Message.user_id.in_([1, 11])  # 用户1和刘童的ID
            ).order_by(Message.created_at.desc()).all()
            
            for msg in user1_liutong_messages:
                sender = db.query(User).filter(User.id == msg.user_id).first()
                sender_name = sender.username if sender else f'用户{msg.user_id}'
                print(f'  - 消息ID: {msg.id}, 发送者: {sender_name}({msg.user_id}), 内容: {str(msg.content)[:50]}..., 时间: {msg.created_at}')
                
            # 查找用户1与testadmin关于这个商品的消息
            print(f'\\n用户1与testadmin关于LG Gram商品的消息:')
            user1_testadmin_messages = db.query(Message).filter(
                Message.item_id == lg_gram_item.id,
                Message.user_id.in_([1, 28])  # 用户1和testadmin的ID
            ).order_by(Message.created_at.desc()).all()
            
            for msg in user1_testadmin_messages:
                sender = db.query(User).filter(User.id == msg.user_id).first()
                sender_name = sender.username if sender else f'用户{msg.user_id}'
                print(f'  - 消息ID: {msg.id}, 发送者: {sender_name}({msg.user_id}), 内容: {str(msg.content)[:50]}..., 时间: {msg.created_at}')
        
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    check_lg_gram()
