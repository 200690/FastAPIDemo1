import ast
import operator

from langchain_core.tools import tool
from agents.common.prebuilt import ToolNode


_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _safe_eval(expr: str):
    tree = ast.parse(expr.strip(), mode="eval")
    return _eval_node(tree.body)


def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        op = _SAFE_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
        return op(_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _SAFE_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
        return op(_eval_node(node.operand))
    raise ValueError(f"不支持的表达式: {type(node).__name__}")


@tool
def search(query: str):
    """搜索互联网信息"""
    return f"关于'{query}'的搜索结果：这是模拟的搜索返回数据。"


@tool
def calculator(expression: str):
    """计算数学表达式，例如 '2 + 3 * 4'"""
    try:
        result = _safe_eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算失败：{e}"


@tool
def get_weather(city: str):
    """查询指定城市的天气"""
    weather_data = {
        "北京": "晴天，25°C，空气质量良好",
        "上海": "多云，28°C，湿度较高",
        "广州": "阵雨，30°C，体感较热",
        "深圳": "阴天，27°C，适宜出行",
    }
    return weather_data.get(city, f"暂无{city}的天气数据")


tools = [search, calculator, get_weather]
tool_node = ToolNode(tools)
