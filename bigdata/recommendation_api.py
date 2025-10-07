#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import subprocess
import json
import sys
import csv
import ast

reload(sys)
sys.setdefaultencoding('utf-8')

def _safe_json_or_list(items_str):
    try:
        return json.loads(items_str)
    except Exception:
        try:
            return ast.literal_eval(items_str)
        except Exception:
            return None

class RecommendationHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj, indent=2, ensure_ascii=False)
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            return self._send_json({'status': 'healthy'}, 200)

        elif self.path.startswith('/recommendations/'):
            user_id = self.path.split('/')[-1]
            
            # 判断是否为AI增强推荐
            is_ai_recommendation = self.path.startswith('/recommendations/ai/')
            if is_ai_recommendation:
                user_id = self.path.split('/')[-1]
                hdfs_path = "/data/output/recommendation_snapshots_ai"
                algorithm = "als_with_ai_enhancement"
                rec_type = "ai_enhanced"
            else:
                hdfs_path = "/data/output/recommendation_snapshots"
                algorithm = "als"
                rec_type = "bigdata"

            # 读取一整条 CSV 记录（跳过表头），确保第二列作为一个字段解析
            cmd = "hadoop fs -cat " + hdfs_path + "/part-* 2>/dev/null | grep -v '^user_id' | grep '^" + user_id + ",\\|^" + user_id + ",\"' | head -1"
            try:
                result = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                result = ""

            line = result.strip()
            if not line:
                return self._send_json({'error': 'User not found'}, 404)

            try:
                # 用 csv.reader 正确解析带引号的第二列
                row_iter = csv.reader([line], delimiter=',', quotechar='"')
                row = next(row_iter)

                uid_str = row[0]
                rec_items_str = row[1]
                algorithm_from_data = row[2] if len(row) > 2 else algorithm
                generated_at = row[3] if len(row) > 3 else None
                expires_at = row[4] if len(row) > 4 else None

                items = _safe_json_or_list(rec_items_str)
                if not isinstance(items, list):
                    raise ValueError('recommended_items is not list')

                items = [int(x) for x in items]

                resp = {
                    'user_id': int(uid_str),
                    'recommendations': items,
                    'algorithm': algorithm_from_data,
                    'type': rec_type,
                    'generated_at': generated_at,
                    'expires_at': expires_at
                }
                
                # 如果是AI增强推荐，添加额外信息
                if is_ai_recommendation:
                    resp['ai_model_version'] = 'bailian-ai-enhanced-v2.0'
                    resp['ai_enhanced'] = True
                
                return self._send_json(resp, 200)

            except Exception as e:
                return self._send_json({
                    'error': 'Invalid data format',
                    'raw': line,
                    'message': str(e)
                }, 422)

        elif self.path.startswith('/ai_recommendations/'):
            # AI增强推荐专用端点
            user_id = self.path.split('/')[-1]
            hdfs_path = "/data/output/recommendation_snapshots_ai"
            
            # 读取一整条 CSV 记录（跳过表头），确保第二列作为一个字段解析
            cmd = "hadoop fs -cat " + hdfs_path + "/part-* 2>/dev/null | grep -v '^user_id' | grep '^" + user_id + ",\\|^" + user_id + ",\"' | head -1"
            try:
                result = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                result = ""

            line = result.strip()
            if not line:
                return self._send_json({'error': 'User not found'}, 404)

            try:
                # 用 csv.reader 正确解析带引号的第二列
                row_iter = csv.reader([line], delimiter=',', quotechar='"')
                row = next(row_iter)

                uid_str = row[0]
                rec_items_str = row[1]
                algorithm = row[2] if len(row) > 2 else "als_with_ai_enhancement"
                generated_at = row[3] if len(row) > 3 else None
                expires_at = row[4] if len(row) > 4 else None

                items = _safe_json_or_list(rec_items_str)
                if not isinstance(items, list):
                    raise ValueError('recommended_items is not list')

                items = [int(x) for x in items]

                resp = {
                    'user_id': int(uid_str),
                    'recommendations': items,
                    'algorithm': algorithm,
                    'type': 'ai_enhanced',
                    'ai_model_version': 'bailian-ai-enhanced-v2.0',
                    'ai_enhanced': True,
                    'generated_at': generated_at,
                    'expires_at': expires_at
                }
                return self._send_json(resp, 200)

            except Exception as e:
                return self._send_json({
                    'error': 'Invalid data format',
                    'raw': line,
                    'message': str(e)
                }, 422)

        elif self.path == '/stats':
            try:
                # 大数据推荐统计
                cmd1 = "hadoop fs -cat /data/output/user_item_scores/part-* 2>/dev/null | wc -l"
                cmd2 = "hadoop fs -cat /data/output/recommendation_snapshots/part-* 2>/dev/null | wc -l"
                cmd3 = "hadoop fs -ls /data/output/user_item_scores/_SUCCESS 2>/dev/null | awk '{print $6, $7, $8}' | head -1"
                
                # AI增强推荐统计
                cmd4 = "hadoop fs -cat /data/output/user_item_scores_ai/part-* 2>/dev/null | wc -l"
                cmd5 = "hadoop fs -cat /data/output/recommendation_snapshots_ai/part-* 2>/dev/null | wc -l"
                cmd6 = "hadoop fs -ls /data/output/user_item_scores_ai/_SUCCESS 2>/dev/null | awk '{print $6, $7, $8}' | head -1"

                count1 = subprocess.check_output(cmd1, shell=True).strip()
                count2 = subprocess.check_output(cmd2, shell=True).strip()
                timestamp1 = subprocess.check_output(cmd3, shell=True).strip()
                
                count3 = subprocess.check_output(cmd4, shell=True).strip()
                count4 = subprocess.check_output(cmd5, shell=True).strip()
                timestamp2 = subprocess.check_output(cmd6, shell=True).strip()

                stats = {
                    'bigdata': {
                        'user_scores_count': int(count1) if count1 else 0,
                        'snapshots_count': int(count2) if count2 else 0,
                        'last_updated': timestamp1 if timestamp1 else "unknown"
                    },
                    'ai_enhanced': {
                        'user_scores_count': int(count3) if count3 else 0,
                        'snapshots_count': int(count4) if count4 else 0,
                        'last_updated': timestamp2 if timestamp2 else "unknown"
                    }
                }
                return self._send_json(stats, 200)
            except Exception:
                return self._send_json({'error': 'stats failed'}, 500)

        else:
            return self._send_json({'error': 'Endpoint not found'}, 404)

    def log_message(self, format, *args):
        try:
            sys.stdout.write("%s - %s\n" % (self.log_date_time_string(), format % args))
        except Exception:
            pass

if __name__ == '__main__':
    PORT = 8080
    server = BaseHTTPServer.HTTPServer(("", PORT), RecommendationHandler)
    print "=" * 50
    print "推荐数据API服务已启动"
    print "服务地址: http://0.0.0.0:%d" % PORT
    print "=" * 50
    print "可用端点:"
    print "  GET /health                           - 健康检查"
    print "  GET /recommendations/<user_id>        - 获取大数据推荐"
    print "  GET /recommendations/ai/<user_id>     - 获取AI增强推荐"
    print "  GET /ai_recommendations/<user_id>     - 获取AI增强推荐（备用端点）"
    print "  GET /stats                            - 获取统计信息"
    print "=" * 50
    print "按 Ctrl+C 停止服务"

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "\n服务已停止"
