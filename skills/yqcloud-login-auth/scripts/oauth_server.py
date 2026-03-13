#!/usr/bin/env python3
"""
YQCloud OAuth 登录认证回调服务器。

启动一个临时 HTTP 服务器，监听 OAuth 回调，提取 access_token 等信息，
存储到 ~/.yqcloud_tmp/ 目录，然后自动关闭。
"""

import http.server
import json
import os
import signal
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

PORT = 49658
TOKEN_DIR = Path.home() / ".yqcloud_tmp"
TOKEN_FILE = TOKEN_DIR / "token.json"

VERIFY_URL = "https://api.yqcloud.com/iam/yqc/users/self"
TENANT_ID = "228549383619211264"

OAUTH_URL = (
    "https://support.yqcloud.com/oauth/oauth/authorize"
    "?response_type=token"
    "&client_id=support"
    "&state="
    "&redirect_uri=" + urllib.parse.quote(f"http://localhost:{PORT}", safe="")
)

CALLBACK_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YQCloud 认证</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #333;
  }
  .card {
    background: #fff; border-radius: 16px; padding: 48px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    text-align: center; max-width: 480px; width: 90%;
  }
  .icon { font-size: 64px; margin-bottom: 16px; }
  h1 { font-size: 24px; margin-bottom: 12px; }
  p { color: #666; font-size: 14px; line-height: 1.6; }
  .success .icon { color: #22c55e; }
  .success h1 { color: #16a34a; }
  .error .icon { color: #ef4444; }
  .error h1 { color: #dc2626; }
  .loading .icon { animation: spin 1s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .detail {
    margin-top: 16px; padding: 12px; background: #f8fafc;
    border-radius: 8px; font-size: 12px; color: #94a3b8;
    word-break: break-all;
  }
</style>
</head>
<body>
<div class="card loading" id="card">
  <div class="icon" id="icon">&#x23F3;</div>
  <h1 id="title">正在处理认证...</h1>
  <p id="message">请稍候</p>
  <div class="detail" id="detail" style="display:none"></div>
</div>
<script>
(function() {
  var hash = window.location.hash.substring(1);
  if (!hash) {
    showError("未收到认证信息", "URL 中没有 token 参数，请重新认证。");
    return;
  }

  var params = {};
  hash.split("&").forEach(function(part) {
    var kv = part.split("=");
    if (kv.length === 2) params[decodeURIComponent(kv[0])] = decodeURIComponent(kv[1]);
  });

  if (!params.access_token) {
    showError("认证失败", "未获取到 access_token，请重新认证。");
    return;
  }

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/callback", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        try {
          var resp = JSON.parse(xhr.responseText);
          if (resp.user_name) {
            showSuccess(params.access_token, resp.user_name);
          } else {
            showSuccess(params.access_token, null);
          }
        } catch(e) {
          showSuccess(params.access_token, null);
        }
      } else {
        showError("存储失败", "无法保存 token，请检查服务端日志。");
      }
    }
  };
  xhr.send(JSON.stringify(params));

  function showSuccess(token, userName) {
    var card = document.getElementById("card");
    card.className = "card success";
    document.getElementById("icon").innerHTML = "&#x2705;";
    document.getElementById("title").textContent = "认证成功";
    var msg = "Token 已保存，您可以关闭此页面。";
    if (userName) msg = "欢迎，" + userName + "！Token 已保存，您可以关闭此页面。";
    document.getElementById("message").textContent = msg;
    var detail = document.getElementById("detail");
    detail.style.display = "block";
    detail.textContent = "access_token: " + token.substring(0, 8) + "..." + token.substring(token.length - 4);
  }

  function showError(title, msg) {
    var card = document.getElementById("card");
    card.className = "card error";
    document.getElementById("icon").innerHTML = "&#x274C;";
    document.getElementById("title").textContent = title;
    document.getElementById("message").textContent = msg;
  }
})();
</script>
</body>
</html>
"""


def verify_token(access_token):
    """调用 YQCloud API 验证 token 有效性，返回用户名或 None。"""
    req = urllib.request.Request(
        VERIFY_URL,
        headers={
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
            "Authorization": f"bearer {access_token}",
            "Content-Type": "application/json",
            "Origin": "https://support.yqcloud.com",
            "Referer": "https://support.yqcloud.com/",
            "X-Tenant-Id": TENANT_ID,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read())
                return data.get("realName") or data.get("loginName") or data.get("email")
    except Exception:
        pass
    return None


class OAuthHandler(http.server.BaseHTTPRequestHandler):
    """处理 OAuth 回调请求。"""

    def do_GET(self):
        """返回 HTML 页面，由前端 JS 提取 hash 中的 token。"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(CALLBACK_HTML.encode("utf-8"))

    def do_POST(self):
        """接收前端 JS 发送的 token 数据并存储。"""
        if self.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            token_data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        # 存储 token
        TOKEN_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(json.dumps(token_data, indent=2, ensure_ascii=False))

        access_token = token_data.get("access_token", "")
        masked = access_token[:8] + "..." + access_token[-4:] if len(access_token) > 12 else "***"
        print(f"\n[OK] Token 已保存到 {TOKEN_FILE}")
        print(f"     access_token: {masked}")
        print(f"     token_type:   {token_data.get('token_type', 'N/A')}")
        print(f"     expires_in:   {token_data.get('expires_in', 'N/A')}")

        # 验证 token 有效性
        response_data = {"status": "ok"}
        user_name = verify_token(access_token)
        if user_name:
            response_data["user_name"] = user_name
            print(f"     用户:         {user_name}")
            print(f"[OK] Token 验证通过")
        else:
            print(f"[WARN] Token 验证失败或无法连接验证服务，token 已保存但未验证")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

        # 延迟关闭服务器，让响应先发送完毕
        threading.Timer(1.0, self.server.shutdown).start()

    def log_message(self, format, *args):
        """安静模式，仅打印关键日志。"""
        pass


def main():
    server = http.server.HTTPServer(("127.0.0.1", PORT), OAuthHandler)

    # 优雅退出
    def signal_handler(sig, frame):
        print("\n[INFO] 收到中断信号，正在关闭服务器...")
        threading.Thread(target=server.shutdown).start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"[INFO] OAuth 回调服务器已启动: http://localhost:{PORT}")
    print(f"[INFO] 正在打开浏览器进行认证...")
    print(f"[INFO] 如果浏览器未自动打开，请手动访问:")
    print(f"       {OAUTH_URL}")
    print(f"[INFO] 等待认证回调中... (Ctrl+C 取消)\n")

    webbrowser.open(OAUTH_URL)

    try:
        server.serve_forever()
    finally:
        server.server_close()
        print("[INFO] 服务器已关闭。")

    # 检查是否成功保存了 token
    if TOKEN_FILE.exists():
        sys.exit(0)
    else:
        print("[ERROR] 未收到认证回调，token 未保存。")
        sys.exit(1)


if __name__ == "__main__":
    main()
