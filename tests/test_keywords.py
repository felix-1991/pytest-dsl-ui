"""测试UI关键字功能

验证pytest-dsl-ui关键字是否正确注册和工作。
"""

import pytest
from unittest.mock import Mock, patch
from pytest_dsl.core.keyword_manager import keyword_manager


class TestUIKeywords:
    """UI关键字测试类"""
    
    def test_keywords_registered(self):
        """测试关键字是否正确注册"""
        # 导入关键字模块，触发注册
        import pytest_dsl_ui
        
        # 验证关键字是否注册
        expected_keywords = [
            '启动浏览器',
            '关闭浏览器',
            '新建页面',
            '切换页面',
            '打开页面',
            '刷新页面',
            '后退',
            '前进',
            '获取页面标题',
            '获取当前地址',
            '点击元素',
            '双击元素',
            '右键点击元素',
            '输入文本',
            '清空文本',
            '选择选项',
            '上传文件',
            '等待元素出现',
            '等待文本出现',
            '获取元素文本',
            '断言元素存在',
            '断言元素不存在',
            '断言元素可见',
            '断言元素启用',
            '断言文本内容',
            '截图',
            '开始录制',
            '停止录制',
            '设置视口大小',
            '获取视口大小',
            '执行JavaScript',
            '设置等待超时',
        ]
        
        registered_keywords = list(keyword_manager._keywords.keys())
        
        for keyword in expected_keywords:
            assert keyword in registered_keywords, f"关键字 '{keyword}' 未注册"
    
    def test_keyword_info_structure(self):
        """测试关键字信息结构"""
        import pytest_dsl_ui
        
        # 测试一个关键字的信息结构
        keyword_info = keyword_manager.get_keyword_info('启动浏览器')
        
        assert keyword_info is not None
        assert 'func' in keyword_info
        assert 'mapping' in keyword_info
        assert 'parameters' in keyword_info
        
        # 验证参数结构
        parameters = keyword_info['parameters']
        assert isinstance(parameters, list)
        
        for param in parameters:
            assert hasattr(param, 'name')
            assert hasattr(param, 'mapping')
            assert hasattr(param, 'description')
    
    @patch('pytest_dsl_ui.core.browser_manager.browser_manager')
    def test_browser_keywords_mock(self, mock_browser_manager):
        """使用Mock测试浏览器关键字"""
        import pytest_dsl_ui
        
        # 模拟浏览器管理器
        mock_browser_manager.launch_browser.return_value = "test_browser_id"
        mock_browser_manager.create_context.return_value = "test_context_id"
        mock_browser_manager.create_page.return_value = "test_page_id"
        
        # 创建模拟上下文
        mock_context = Mock()
        
        # 测试启动浏览器关键字
        result = keyword_manager.execute('启动浏览器', 
                                       browser_type='chromium',
                                       headless=True,
                                       context=mock_context)
        
        # 验证返回格式
        assert isinstance(result, dict)
        assert 'result' in result
        assert 'captures' in result
        assert 'session_state' in result
        assert 'metadata' in result
        
        # 验证浏览器管理器被调用
        mock_browser_manager.launch_browser.assert_called_once()
        mock_browser_manager.create_context.assert_called_once()
        mock_browser_manager.create_page.assert_called_once()
    
    def test_register_keywords_function(self):
        """测试register_keywords函数"""
        import pytest_dsl_ui
        
        # 创建模拟的关键字管理器
        mock_manager = Mock()
        
        # 调用register_keywords函数
        pytest_dsl_ui.register_keywords(mock_manager)
        
        # 验证函数执行成功（不抛出异常）
        assert True
    
    def test_keyword_parameter_mapping(self):
        """测试关键字参数映射"""
        import pytest_dsl_ui
        
        # 测试点击元素关键字的参数映射
        keyword_info = keyword_manager.get_keyword_info('点击元素')
        mapping = keyword_info['mapping']
        
        # 验证关键参数映射
        assert '定位器' in mapping
        assert mapping['定位器'] == 'selector'
        assert '超时时间' in mapping
        assert mapping['超时时间'] == 'timeout'
    
    def test_assertion_keywords_structure(self):
        """测试断言关键字结构"""
        import pytest_dsl_ui
        
        assertion_keywords = [
            '断言元素存在',
            '断言元素不存在', 
            '断言元素可见',
            '断言元素启用',
            '断言文本内容'
        ]
        
        for keyword in assertion_keywords:
            keyword_info = keyword_manager.get_keyword_info(keyword)
            assert keyword_info is not None
            
            # 验证断言关键字都有定位器参数
            mapping = keyword_info['mapping']
            assert '定位器' in mapping
            assert mapping['定位器'] == 'selector'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
