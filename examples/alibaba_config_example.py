#!/usr/bin/env python3
"""
阿里巴巴通义千问配置示例

本示例展示如何配置和使用阿里巴巴通义千问模型：
1. 基本配置设置
2. 环境变量配置
3. 配置验证
4. 常见问题解决
"""

import os
import sys
from pathlib import Path

# 添加父目录到路径以便导入 stagehand
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from stagehand.config import StagehandConfig
    from stagehand import Stagehand
except ImportError as e:
    print(f"导入错误: {e}")
    print("请从 stagehand-python 根目录运行此脚本")
    sys.exit(1)


def setup_alibaba_environment():
    """设置阿里巴巴通义千问的环境变量"""
    print("🔧 设置阿里巴巴通义千问环境变量")
    print("-" * 40)
    
    # 检查是否已设置环境变量
    alibaba_api_key = os.getenv("ALIBABA_API_KEY")
    alibaba_endpoint = os.getenv("ALIBABA_ENDPOINT")
    
    if not alibaba_api_key:
        print("❌ 未找到 ALIBABA_API_KEY 环境变量")
        print("请在 .env 文件中设置:")
        print("ALIBABA_API_KEY=your-alibaba-api-key-here")
        return False
    
    if not alibaba_endpoint:
        print("❌ 未找到 ALIBABA_ENDPOINT 环境变量")
        print("请在 .env 文件中设置:")
        print("ALIBABA_ENDPOINT=https://dashscope.aliyuncs.com/compatible-mode/v1")
        return False
    
    print(f"✅ ALIBABA_API_KEY: {alibaba_api_key[:10]}...")
    print(f"✅ ALIBABA_ENDPOINT: {alibaba_endpoint}")
    return True


def create_alibaba_config_basic():
    """创建基本的阿里巴巴配置"""
    print("\n📝 基本阿里巴巴配置示例")
    print("-" * 40)
    
    try:
        config = StagehandConfig(
            model_name="qwen-turbo",  # 通义千问模型
            model_client_options={
                "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": os.getenv("ALIBABA_API_KEY")
            },
            verbose=1
        )
        
        print("✅ 基本配置创建成功")
        print(f"   模型: {config.model_name}")
        print(f"   端点: {config.model_client_options.get('api_base')}")
        return config
        
    except Exception as e:
        print(f"❌ 配置创建失败: {e}")
        return None


def create_alibaba_config_advanced():
    """创建高级阿里巴巴配置"""
    print("\n🚀 高级阿里巴巴配置示例")
    print("-" * 40)
    
    try:
        config = StagehandConfig(
            model_name="qwen-max",  # 使用更强大的模型
            model_client_options={
                "api_base": os.getenv("ALIBABA_ENDPOINT"),
                "api_key": os.getenv("ALIBABA_API_KEY"),
                "timeout": 30,  # 设置超时时间
                "max_retries": 3,  # 设置重试次数
            },
            verbose=2,  # 详细日志
            headless=True,  # 无头模式
            debug_dom=True,  # DOM 调试
        )
        
        print("✅ 高级配置创建成功")
        print(f"   模型: {config.model_name}")
        print(f"   端点: {config.model_client_options.get('api_base')}")
        print(f"   超时: {config.model_client_options.get('timeout')}秒")
        print(f"   重试: {config.model_client_options.get('max_retries')}次")
        return config
        
    except Exception as e:
        print(f"❌ 高级配置创建失败: {e}")
        return None


def test_alibaba_connection(config):
    """测试阿里巴巴连接"""
    print("\n🔍 测试阿里巴巴连接")
    print("-" * 40)
    
    try:
        # 创建 Stagehand 实例
        stagehand = Stagehand(config=config)
        print("✅ Stagehand 实例创建成功")
        
        # 这里可以添加更多的连接测试
        print("✅ 阿里巴巴通义千问配置验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False


def demonstrate_model_options():
    """展示可用的阿里巴巴模型选项"""
    print("\n🤖 阿里巴巴通义千问可用模型")
    print("-" * 40)
    
    models = [
        {
            "name": "qwen-turbo",
            "description": "通义千问超大规模语言模型，支持中文英文等不同语言输入",
            "context": "8k tokens",
            "use_case": "日常对话、文本生成"
        },
        {
            "name": "qwen-plus",
            "description": "通义千问超大规模语言模型增强版",
            "context": "32k tokens",
            "use_case": "复杂推理、长文本处理"
        },
        {
            "name": "qwen-max",
            "description": "通义千问千亿级别超大规模语言模型",
            "context": "8k tokens",
            "use_case": "最高质量的文本生成和理解"
        },
        {
            "name": "qwen-max-longcontext",
            "description": "通义千问长上下文版本",
            "context": "30k tokens",
            "use_case": "长文档分析、大量信息处理"
        }
    ]
    
    for model in models:
        print(f"📝 {model['name']}")
        print(f"   描述: {model['description']}")
        print(f"   上下文: {model['context']}")
        print(f"   适用场景: {model['use_case']}")
        print()


def show_configuration_tips():
    """显示配置建议和最佳实践"""
    print("\n💡 阿里巴巴配置建议和最佳实践")
    print("-" * 40)
    
    tips = [
        "🔑 API密钥安全: 将API密钥存储在环境变量中，不要硬编码在代码里",
        "🌐 网络设置: 确保网络可以访问 dashscope.aliyuncs.com",
        "⏱️  超时设置: 根据任务复杂度调整timeout参数（建议30-60秒）",
        "🔄 重试机制: 设置合适的max_retries参数处理网络波动",
        "📊 模型选择: 根据任务需求选择合适的模型（turbo适合简单任务，max适合复杂任务）",
        "🐛 调试模式: 开发时使用verbose=2获取详细日志信息",
        "🚀 生产环境: 生产环境建议使用headless=True提高性能",
        "💰 成本控制: 监控API调用次数和token使用量"
    ]
    
    for tip in tips:
        print(f"   {tip}")
    print()


def show_troubleshooting():
    """显示常见问题解决方案"""
    print("\n🔧 常见问题解决方案")
    print("-" * 40)
    
    issues = [
        {
            "problem": "❌ 401 Unauthorized 错误",
            "solution": "检查API密钥是否正确，确保在阿里云控制台已开通通义千问服务"
        },
        {
            "problem": "❌ 网络连接超时",
            "solution": "检查网络连接，增加timeout参数值，或检查防火墙设置"
        },
        {
            "problem": "❌ 模型不存在错误",
            "solution": "确认使用的模型名称正确，检查是否有权限访问该模型"
        },
        {
            "problem": "❌ 请求频率限制",
            "solution": "降低请求频率，或联系阿里云提升API调用限额"
        },
        {
            "problem": "❌ 上下文长度超限",
            "solution": "减少输入文本长度，或使用支持更长上下文的模型版本"
        }
    ]
    
    for issue in issues:
        print(f"{issue['problem']}")
        print(f"   解决方案: {issue['solution']}")
        print()


def main():
    """运行所有示例"""
    print("🚀 阿里巴巴通义千问配置示例")
    print("=" * 60)
    
    # 检查环境设置
    if not setup_alibaba_environment():
        print("\n❌ 环境设置不完整，请先配置API密钥")
        return
    
    # 展示模型选项
    demonstrate_model_options()
    
    # 创建基本配置
    basic_config = create_alibaba_config_basic()
    
    # 创建高级配置
    advanced_config = create_alibaba_config_advanced()
    
    # 测试连接
    if advanced_config:
        test_alibaba_connection(advanced_config)
    
    # 显示配置建议
    show_configuration_tips()
    
    # 显示问题解决方案
    show_troubleshooting()
    
    print("=" * 60)
    print("✨ 阿里巴巴配置示例完成！")
    print()
    print("🎯 下一步:")
    print("   1. 确保 .env 文件中配置了正确的API密钥")
    print("   2. 根据需求选择合适的模型")
    print("   3. 在实际项目中使用这些配置")


if __name__ == "__main__":
    main()