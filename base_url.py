# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, Response
import requests
from datetime import datetime


app = Flask(__name__)


# OpenAI API的基础URL
openai_api_base_url = "https://api.openai.com"


@app.route('/proxy/<path:endpoint>', methods=['POST'])
def proxy(endpoint):
    try:
        # 获取客户端发送的JSON数据
        client_data = request.json
        if not client_data:
            return jsonify({"error": "Request JSON data is missing"}), 400

        # 获取角色为'user'的所有消息
        user_messages = [message for message in client_data['messages'] if message['role'] == 'user']
        last_user_message = user_messages[-1]
        print(last_user_message)

        ss_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = {"text":last_user_message.get("content"),"time":ss_now}

        with open('./msg.txt', 'a', encoding='utf-8') as file:
            file.write(str(text) + '\n')


        ss = request.headers
        print("Client headers:",ss)


        # 构建请求头
        headers = {
            "Authorization": request.headers.get('Authorization'),
            "Content-Type": "application/json"
        }

        # 构建实际要请求的OpenAI API的完整URL
        openai_url = f"{openai_api_base_url}/{endpoint}"

        # 向 OpenAI API 发送流式请求
        response = requests.post(url=openai_url, headers=headers, json=client_data, stream=True)

        def generate():
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk

        return Response(generate(), content_type=response.headers['content-type'])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=33322)