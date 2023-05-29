import os
from flask import Flask, request

app = Flask(__name__)


@app.route('/test', methods=['GET'])
def test():
    summary = 'hello'
    print(summary)
    # return json.dumps({'success': True, 'summary': summary})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)