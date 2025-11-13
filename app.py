import os
from flask import Flask, jsonify, request, render_template
from datetime import datetime

# --- 절대 경로 기반 Flask 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))

# --- 간단한 메모리 DB ---
todos = {}
next_id = 1

# --- 미들웨어: 요청 로그 ---
@app.before_request
def log_request():
    print(f"[{datetime.now()}] {request.method} {request.path}")

# --- 응답 포맷 함수 ---
def response(status: str, data=None, message=None):
    return jsonify({
        "status": status,
        "data": data,
        "message": message
    })

# ---------------- POST ----------------

# 1️⃣ 할 일 추가
@app.route('/todos', methods=['POST'])
def create_todo():
    global next_id
    data = request.get_json()
    if not data or 'title' not in data:
        return response("error", None, "Title is required"), 400
    
    todo = {"id": next_id, "title": data['title'], "done": False}
    todos[next_id] = todo
    next_id += 1
    return response("success", todo, "Todo created"), 201

# 2️⃣ 여러 개 추가
@app.route('/todos/bulk', methods=['POST'])
def create_bulk_todos():
    data = request.get_json()
    if not isinstance(data, list):
        return response("error", None, "Expected a list of todos"), 400
    
    created = []
    global next_id
    for item in data:
        todo = {"id": next_id, "title": item.get("title", "Untitled"), "done": False}
        todos[next_id] = todo
        created.append(todo)
        next_id += 1
    return response("success", created, "Todos created"), 201

# ---------------- GET ----------------

# 3️⃣ 전체 조회
@app.route('/todos', methods=['GET'])
def get_all_todos():
    return response("success", list(todos.values())), 200

# 4️⃣ 특정 ID 조회
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = todos.get(todo_id)
    if not todo:
        return response("error", None, "Todo not found"), 404
    return response("success", todo), 200

# ---------------- PUT ----------------

# 5️⃣ 특정 할 일 수정
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = todos.get(todo_id)
    if not todo:
        return response("error", None, "Todo not found"), 404
    
    data = request.get_json()
    todo['title'] = data.get('title', todo['title'])
    todo['done'] = data.get('done', todo['done'])
    return response("success", todo, "Todo updated"), 200

# 6️⃣ 모든 할 일 완료 처리
@app.route('/todos/complete_all', methods=['PUT'])
def complete_all_todos():
    for todo in todos.values():
        todo['done'] = True
    return response("success", list(todos.values()), "All todos completed"), 200

# ---------------- DELETE ----------------

# 7️⃣ 특정 할 일 삭제
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    if todo_id not in todos:
        return response("error", None, "Todo not found"), 404
    deleted = todos.pop(todo_id)
    return response("success", deleted, "Todo deleted"), 200

# 8️⃣ 전체 삭제
@app.route('/todos', methods=['DELETE'])
def delete_all_todos():
    todos.clear()
    return response("success", None, "All todos deleted"), 200

# ---------------- 5xx 에러 테스트 ----------------

@app.route('/error', methods=['GET'])
def trigger_error():
    try:
        1 / 0
    except Exception as e:
        return response("error", None, f"Internal Server Error: {str(e)}"), 500

# ---------------- HTML 렌더링 ----------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------------- 서버 실행 ----------------

if __name__ == '__main__':
    print("현재 작업 디렉토리:", os.getcwd())
    print("템플릿 폴더 절대 경로:", os.path.abspath(app.template_folder))
    app.run(debug=True)
