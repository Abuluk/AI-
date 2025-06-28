<template>
  <div class="comment-section">
    <div v-if="comments.length === 0" class="empty">暂无评论，快来抢沙发吧！</div>
    <div v-for="comment in comments" :key="comment.id" class="comment-item">
      <!-- 一级评论 -->
      <div class="comment-main">
        <span class="user">{{ comment.user_name }}</span>
        <span class="content">{{ comment.content }}</span>
        <button class="reply-btn" @click="setReply(comment)">回复</button>
        <button v-if="canDelete(comment)" class="delete-btn" @click="deleteComment(comment.id)">删除</button>
        <button v-if="comment.children && comment.children.length > 0" class="expand-btn" @click="toggleExpand(comment.id)">
          {{ expandedComments[comment.id] ? '收起回复' : '展开回复' }} ({{ comment.children.length }})
        </button>
        <!-- 点赞按钮 -->
        <button class="like-btn" :class="{ liked: comment.liked_by_me }" @click="handleLike(comment)">
          👍 {{ comment.like_count || 0 }}
        </button>
      </div>
      <!-- 二级评论及其所有回复 -->
      <div class="comment-children" v-if="expandedComments[comment.id] && comment.children && comment.children.length">
        <div v-for="child in comment.children" :key="child.id" class="comment-child">
          <span class="user">{{ child.user_name }}</span>
          <span v-if="child.reply_to_user_name" class="at-highlight">@{{ child.reply_to_user_name }}</span>
          <span class="content">{{ child.content }}</span>
          <button class="reply-btn" @click="setReply(child)">回复</button>
          <button v-if="canDelete(child)" class="delete-btn" @click="deleteComment(child.id)">删除</button>
          <!-- 点赞按钮 -->
          <button class="like-btn" :class="{ liked: child.liked_by_me }" @click="handleLike(child)">
            👍 {{ child.like_count || 0 }}
          </button>
        </div>
      </div>
    </div>
    <!-- 评论输入框 -->
    <div class="comment-input">
      <textarea v-model="inputContent" placeholder="写下你的评论..." />
      <button class="submit-btn" @click="handleSubmit">发布</button>
      <span v-if="replyingTo" class="replying-tip">正在回复 @{{ replyingTo.user_name }} <button @click="cancelReply">取消</button></span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/store/auth'

const props = defineProps({
  itemId: Number,
  buyRequestId: Number,
  currentUser: Object,
  isOwner: Boolean
})

const comments = ref([])
const inputContent = ref('')
const replyingTo = ref(null)
const replyParentId = ref(null)
const replyToUserId = ref(null)
const expandedComments = ref({})
const likeLoading = ref({})

const fetchComments = async () => {
  const params = props.itemId ? { item_id: props.itemId } : { buy_request_id: props.buyRequestId }
  // 用tree接口，返回树结构+点赞状态
  const res = await api.getCommentTree(params)
  comments.value = res.data
}

const handleLike = async (comment) => {
  if (likeLoading.value[comment.id]) return;
  likeLoading.value[comment.id] = true;
  try {
    if (!comment.liked_by_me) {
      await api.likeComment(comment.id);
    } else {
      await api.unlikeComment(comment.id);
    }
    await fetchComments(); // 点赞后强制刷新，保证点赞数和高亮状态同步
  } catch (e) {}
  likeLoading.value[comment.id] = false;
}

const handleSubmit = async () => {
  if (!inputContent.value.trim()) return
  await api.createComment({
    content: inputContent.value,
    item_id: props.itemId,
    buy_request_id: props.buyRequestId,
    parent_id: replyParentId.value,
    reply_to_user_id: replyToUserId.value
  })
  inputContent.value = ''
  replyingTo.value = null
  replyParentId.value = null
  replyToUserId.value = null
  await fetchComments()
}

const setReply = (comment) => {
  replyingTo.value = comment
  replyParentId.value = comment.id
  replyToUserId.value = comment.user_id
  inputContent.value = ''
}

const cancelReply = () => {
  replyingTo.value = null
  replyParentId.value = null
  replyToUserId.value = null
  inputContent.value = ''
}

const canDelete = (comment) => {
  // 只有评论作者或商品/求购发布者能删除
  if (!props.currentUser) return false
  if (props.currentUser.id === comment.user_id) return true
  // 商品/求购发布者
  if (props.isOwner) return true
  return false
}

const deleteComment = async (commentId) => {
  await api.deleteComment(commentId)
  await fetchComments()
}

const toggleExpand = (id) => {
  expandedComments.value[id] = !expandedComments.value[id]
}

onMounted(fetchComments)
watch(() => [props.itemId, props.buyRequestId], fetchComments)
</script>

<style scoped>
.comment-section {
  margin-top: 30px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  max-height: 400px;
  overflow-y: auto;
}
.comment-item {
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 0;
}
.comment-main, .comment-child, .comment-reply {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.user {
  font-weight: 600;
  color: #1976d2;
}
.content {
  flex: 1;
  color: #333;
}
.reply-btn, .delete-btn, .submit-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.95em;
  margin-left: 8px;
}
.reply-btn:hover, .delete-btn:hover, .submit-btn:hover {
  text-decoration: underline;
}
.comment-children, .comment-replies {
  margin-left: 32px;
}
.comment-input {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
textarea {
  width: 100%;
  min-height: 60px;
  border-radius: 6px;
  border: 1px solid #ddd;
  padding: 8px;
  font-size: 1em;
  resize: vertical;
}
.replying-tip {
  color: #888;
  font-size: 0.95em;
  margin-left: 8px;
}
.empty {
  color: #aaa;
  text-align: center;
  margin-bottom: 16px;
}
.at-highlight {
  color: #e67e22;
  font-weight: bold;
  margin: 0 2px;
}
.expand-btn {
  margin-left: 10px;
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.95em;
}
.like-btn {
  margin-left: 10px;
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 1em;
  transition: color 0.2s;
}
.like-btn.liked {
  color: #e67e22;
  font-weight: bold;
}
</style> 