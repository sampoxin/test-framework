"""
pytest 模式专用 conftest（供未来 pytest 集成使用）
使用 python -m minium 运行时，此文件不生效
"""
# 当前阶段 Minium 测试使用 python -m minium 运行，pytest 集成后续按需启用
# import pytest
# import minium
#
# @pytest.fixture(scope="session")
# def mini_test():
#     """初始化 Minium，整个测试会话共享一个小程序实例"""
#     app = minium.Minium("mini/config.json")
#     yield app
