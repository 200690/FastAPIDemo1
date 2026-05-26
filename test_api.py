import urllib.request, urllib.parse, json, sys
sys.stdout.reconfigure(encoding='utf-8')
base = 'http://127.0.0.1:8000'

def test(name, path):
    try:
        req = urllib.request.urlopen(base + path)
        result = json.loads(req.read())
        resp = result.get("response", "")[:80]
        print(f"[OK] {name}: {resp}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")

print("=== LangGraph 实战 API 测试 ===\n")

print("1. 根路径")
req = urllib.request.urlopen(f'{base}/')
print(json.loads(req.read()))

msg = urllib.parse.quote("你好")
test("基础聊天", f'/api/chat/basic?message={msg}')

msg = urllib.parse.quote("北京的天气怎么样")
test("工具调用", f'/api/chat/tool?message={msg}')

msg = urllib.parse.quote("我叫小明")
test("持久化记忆", f'/api/chat/memory?message={msg}&thread_id=session1')

msg = urllib.parse.quote("如何搭建微服务架构")
test("多Agent协作", f'/api/chat/advanced?message={msg}')

msg = urllib.parse.quote("计算2+3*4")
test("人机审批", f'/api/chat/human?message={msg}&approve=true')

print("\n=== 测试完成 ===")
