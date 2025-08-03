#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试执行器 - 修复编码问题版本
"""

import asyncio
import logging
import time
import json
import subprocess
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

# 导入简化测试模块
from simplified_automation_test import SimplifiedAutomationTester


async def run_automation_test_with_encoding_fix():
    """运行自动化测试（修复编码问题）"""
    try:
        logger.info("=" * 60)
        logger.info("开始全面用户故事自动化测试")
        logger.info("=" * 60)
        
        tester = SimplifiedAutomationTester()
        result = await tester.run_simplified_automation_test()
        
        logger.info("=" * 60)
        logger.info("自动化测试报告")
        logger.info("=" * 60)
        
        success_symbol = "✓" if result.get('overall_success') else "✗"
        logger.info(f"总体结果: {success_symbol}")
        logger.info(f"测试时长: {result.get('test_summary', {}).get('duration_minutes', 0):.1f}分钟")
        
        # 功能测试状态
        functional_assessment = result.get("functional_assessment", {})
        func_symbol = "✓" if functional_assessment.get('success') else "✗"
        logger.info(f"功能测试: {func_symbol}")
        logger.info(f"通过测试: {functional_assessment.get('passed_tests', 0)}/{functional_assessment.get('total_tests', 0)}")
        
        # API测试状态
        api_assessment = result.get("api_assessment", {})
        if api_assessment.get("skipped"):
            logger.info("API测试: 已跳过（服务不可用）")
        else:
            api_symbol = "✓" if api_assessment.get('success') else "✗"
            logger.info(f"API测试: {api_symbol}")
        
        # 服务状态
        service_assessment = result.get("service_assessment", {})
        service_symbol = "✓" if service_assessment.get('available') else "✗"
        logger.info(f"服务可用: {service_symbol}")
        
        # 系统就绪状态
        system_readiness = result.get("system_readiness", {})
        logger.info("系统就绪状态:")
        for check, status in system_readiness.items():
            symbol = "✓" if status else "✗"
            logger.info(f"  {check}: {symbol}")
        
        logger.info("建议:")
        for rec in result.get("recommendations", []):
            logger.info(f"  • {rec}")
        
        logger.info("下一步:")
        for step in result.get("next_steps", []):
            logger.info(f"  {step}")
        
        logger.info("=" * 60)
        
        return result.get("overall_success", False)
        
    except Exception as e:
        logger.error(f"自动化测试执行失败: {e}")
        return False


def main():
    """主函数"""
    try:
        success = asyncio.run(run_automation_test_with_encoding_fix())
        
        if success:
            print("\n🎉 自动化测试全部通过！")
            print("系统已就绪，可以进行用户验收测试。")
        else:
            print("\n⚠️ 部分测试未通过，请查看详细报告。")
            print("建议修复问题后重新运行测试。")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n测试执行异常: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)