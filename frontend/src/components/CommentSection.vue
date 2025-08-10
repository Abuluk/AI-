<template>
  <div class="comment-section">
    <div class="comments-container">
      <div v-if="comments.length === 0" class="empty">暂无评论，快来抢沙发吧！</div>
      <template v-for="comment in comments" :key="comment.id">
        <div class="comment-item">
          <div class="comment-row">
            <div class="comment-main">
              <span class="user">{{ comment.user_name }}：</span>
              <span class="content">{{ comment.content }}</span>
            </div>
            <div class="comment-actions">
              <button class="reply-btn" @click="setReply(comment)">回复</button>
              <button v-if="canDelete(comment)" class="delete-btn" @click="deleteComment(comment.id)">删除</button>
              <button v-if="comment.children && comment.children.length > 0" class="expand-btn" @click="toggleExpand(comment.id)">{{ expandedComments[comment.id] ? '收起回复' : '展开回复' }} ({{ comment.children.length }})</button>
              <button class="like-btn" :class="{ liked: comment.liked_by_me }" @click="handleLike(comment)"><i class="fas fa-thumbs-up"></i> {{ comment.like_count || 0 }}</button>
            </div>
          </div>
          <div v-if="comment.children && comment.children.length > 0 && expandedComments[comment.id]" class="comment-children">
            <CommentNode v-for="child in comment.children" :key="child.id" :comment="child" />
          </div>
        </div>
      </template>
    </div>
    <div class="comment-input-fixed">
      <div class="comment-input">
        <textarea v-model="inputContent" placeholder="写下你的评论..." />
        <div class="submit-container">
          <button class="submit-btn" @click="handleSubmit">
            <i class="fas fa-paper-plane"></i>
            <span>发布评论</span>
          </button>
        </div>
        <span v-if="replyingTo" class="replying-tip">正在回复 @{{ replyingTo.user_name }} <button @click="cancelReply">取消</button></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comment-section {
  margin-top: 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  position: relative;
  display: flex;
  flex-direction: column;
  height: 650px;
}

.comments-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px 10px 0 10px;
  max-height: calc(100% - 70px);
}

.comment-input-fixed {
  position: sticky;
  bottom: 0;
  background: #fff;
  border-top: 1px solid #eee;
  padding: 10px 10px 8px 10px;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
  z-index: 10;
}

.comment-item {
  background: #fff;
  border-radius: 8px;
  box-shadow: none;
  border: 1px solid #eee;
  margin-bottom: 18px;
  padding: 16px;
  transition: all 0.2s ease;
  position: relative;
}
.comment-item:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  border-color: #e0e0e0;
}
.comment-row {
  display: flex;
  align-items: flex-start;
  width: 100%;
}
.comment-main {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex: 1 1 auto;
  min-width: 0;
  gap: 8px;
}
.user {
  font-weight: 700;
  color: #42b983;
  font-size: 1.02em;
  margin-right: 8px;
  white-space: nowrap;
}
.content {
  color: #333;
  font-size: 1em;
  text-align: left;
  word-break: break-all;
  flex: 1;
  min-width: 0;
  line-height: 1.6;
  padding: 4px 0;
}
.comment-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
  white-space: nowrap;
  margin-top: 8px;
}
:deep(.comment-actions), :deep(.comment-children .comment-actions) {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  margin-left: auto !important;
  white-space: nowrap !important;
  justify-content: flex-end !important;
}
:deep(.comment-actions > button), :deep(.reply-btn), :deep(.delete-btn), :deep(.expand-btn), :deep(.like-btn) {
  padding: 4px 10px !important;
  font-size: 0.9em !important;
  min-width: 0 !important;
  max-width: none !important;
  height: 28px;
  border-radius: 4px !important;
  transition: all 0.2s;
  background-color: transparent !important;
  border: 1px solid #ddd !important;
  color: #666 !important;
}
:deep(.comment-actions > button):hover {
  background-color: #f5f5f5 !important;
  border-color: #ccc !important;
  color: #333 !important;
}
:deep(.like-btn) {
  padding: 4px 10px !important;
}
:deep(.like-btn.liked) {
  color: #42b983 !important;
  font-weight: bold;
  border-color: #42b983 !important;
  background-color: rgba(66, 185, 131, 0.1) !important;
}
.comment-children {
  margin-left: 30px;
  margin-top: 12px;
  border-left: 1px solid #eee;
  padding-left: 16px;
}
.comment-input {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.comment-input .submit-container {
  display: flex;
  justify-content: center;
  width: 100%;
  margin-top: 6px;
}
:deep(.submit-btn) {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px !important;
  padding: 8px 18px !important;
  font-size: 1em !important;
  min-width: 90px !important;
  background: linear-gradient(135deg, #42b983 0%, #2d8659 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(66, 185, 131, 0.18);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.10);
  font-weight: 600;
}
:deep(.submit-btn):hover {
  background: linear-gradient(135deg, #39ac78 0%, #287950 100%) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(66, 185, 131, 0.22);
}
:deep(.submit-btn):active {
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(66, 185, 131, 0.15);
}
:deep(.submit-btn):focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.18);
}
:deep(.submit-btn i) {
  font-size: 0.9em;
}
textarea {
  width: 100%;
  min-height: 40px;
  border-radius: 6px;
  border: 1px solid #ddd;
  padding: 8px;
  font-size: 1em;
  resize: vertical;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  line-height: 1.5;
}
textarea:focus {
  border: 1px solid #42b983 !important;
  outline: none;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.1);
}
.replying-tip {
  color: #888;
  font-size: 0.9em;
  margin-left: 8px;
  padding-top: 2px;
}
.empty {
  color: #aaa;
  text-align: center;
  margin-bottom: 10px;
  font-size: 1em;
  padding: 10px 0;
  background-color: #f9f9f9;
  border-radius: 8px;
}
.at-highlight {
  color: #e67e22;
  font-weight: bold;
  margin: 0 2px;
}
</style>

<script setup>
import { ref, watch, onMounted, defineComponent, h } from 'vue'
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
    await fetchComments();
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
  if (!props.currentUser) return false
  if (props.currentUser.id === comment.user_id) return true
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

// 递归组件
const CommentNode = defineComponent({
  name: 'CommentNode',
  props: { comment: Object },
  setup(props) {
    return () => h('div', { class: 'comment-item' }, [
      h('div', { class: 'comment-row' }, [
        h('div', { class: 'comment-main' }, [
          h('span', { class: 'user' }, props.comment.user_name + '：'),
          h('span', { class: 'content' }, props.comment.content)
        ]),
        h('div', { class: 'comment-actions' }, [
          h('button', { class: 'reply-btn', onClick: () => setReply(props.comment) }, '回复'),
          canDelete(props.comment) ? h('button', { class: 'delete-btn', onClick: () => deleteComment(props.comment.id) }, '删除') : null,
          (props.comment.children && props.comment.children.length > 0) ?
            h('button', {
              class: 'expand-btn',
              onClick: () => toggleExpand(props.comment.id)
            }, `${expandedComments.value[props.comment.id] ? '收起回复' : '展开回复'} (${props.comment.children.length})`) : null,
          h('button', {
            class: ['like-btn', props.comment.liked_by_me ? 'liked' : ''],
            onClick: () => handleLike(props.comment)
          }, [
            h('i', { class: ['fas', 'fa-thumbs-up'] }),
            ` ${props.comment.like_count || 0}`
          ])
        ])
      ]),
      (props.comment.children && props.comment.children.length > 0 && expandedComments.value[props.comment.id]) ?
        h('div', { class: 'comment-children' },
          props.comment.children.map(child => h(CommentNode, { comment: child, key: child.id }))
        ) : null
    ])
  }
})
</script>