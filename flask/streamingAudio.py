from flask import Flask, request, Response
import io
import time

app = Flask(__name__)

# 模拟生成半句半句音频数据的函数
def generate_audio_data():
    # 这里只是一个示例，实际上你需要根据你的需求生成音频数据
    chunk1 = b'chunk1_audio_data'
    chunk2 = b'chunk2_audio_data'
    # 通过yield逐步返回音频数据
    yield chunk1
    time.sleep(1)  # 模拟处理时间
    yield chunk2

# 路由处理函数，用于处理音频流请求
@app.route('/stream_audio', methods=['GET'])
def stream_audio():
    # 返回一个流式响应
    return Response(generate_audio_data(), mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
