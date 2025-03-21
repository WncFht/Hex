# encoding: utf-8
import subprocess
import os
import sys
import webbrowser
import time
import traceback

# 创建logs目录
os.makedirs('logs', exist_ok=True)

def install_dependencies():
    """安装必要的依赖"""
    print("正在安装必要的依赖...")
    try:
        # 安装Flask和Flask-CORS
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors'])
        print("依赖安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {str(e)}")
        return False

def start_app():
    """启动Hex棋盘应用程序"""
    print("正在启动 Hex 棋盘应用程序...")
    
    # 打开日志文件
    log_file = open('logs/flask.log', 'a', encoding='utf-8')
    
    try:
        # 启动Flask服务器
        flask_process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=log_file,
            stderr=log_file,
            text=True,
            encoding='utf-8'
        )
        
        # 等待服务器启动
        print("等待服务器启动(3秒)...")
        time.sleep(3)
        
        # 检查进程是否已终止
        if flask_process.poll() is not None:
            print("服务器启动失败！")
            if os.path.exists('logs/flask.log'):
                with open('logs/flask.log', 'r', encoding='utf-8') as f:
                    print("错误日志:")
                    print(f.read())
            return False
        
        # 打开浏览器
        print("启动浏览器...")
        webbrowser.open('http://localhost:5000')
        print("Hex 棋盘应用程序已启动！")
        print("请在浏览器中访问: http://localhost:5000")
        print("按 Ctrl+C 停止服务器")
        
        # 保持程序运行
        try:
            while True:
                time.sleep(1)
                if flask_process.poll() is not None:
                    print("服务器已停止运行")
                    break
        except KeyboardInterrupt:
            print("\n正在关闭服务器...")
            flask_process.terminate()
            flask_process.wait()
            print("启动被用户中断，正在退出...")
        
        return True
    except Exception as e:
        print(f"启动应用程序时出错: {str(e)}")
        print(traceback.format_exc())
        return False
    finally:
        log_file.close()

if __name__ == "__main__":
    # 检查是否安装了依赖
    if not (os.path.exists(os.path.join(sys.prefix, 'Lib', 'site-packages', 'flask')) or 
            os.path.exists(os.path.join(sys.prefix, 'lib', 'python' + sys.version[:3], 'site-packages', 'flask'))):
        if not install_dependencies():
            sys.exit(1)
    
    # 启动应用程序
    if not start_app():
        sys.exit(1) 