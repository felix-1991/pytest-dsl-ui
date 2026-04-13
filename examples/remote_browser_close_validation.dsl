@name: "远程浏览器关闭验证"
@description: "验证 pytest-dsl 远程关键字模式下，启动浏览器后再关闭浏览器不会因跨线程触发 Playwright greenlet 错误"
@remote: "http://localhost:8273/" as orbitest_debug_server

orbitest_debug_server|[启动浏览器], 浏览器: "chromium", 无头模式: True
orbitest_debug_server|[关闭浏览器]
