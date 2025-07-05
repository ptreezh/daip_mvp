import os
import sys
from typing import Any

import yaml
from pydantic import ValidationError

# 添加schemas目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from schemas.protocol_schema import ProtocolModel


def validate_protocol(yaml_content: str) -> dict[str, Any]:
    """验证YAML字符串是否符合DAIP协议模式。
    检查YAML语法和结构正确性。

    Args:
    ----
        yaml_content: YAML内容字符串

    Returns:
    -------
        包含成功或失败信息的字典

    """
    try:
        # 1. 检查YAML语法是否正确
        data = yaml.safe_load(yaml_content)
        if not isinstance(data, dict):
            return {
                "success": False,
                "error": "YAML does not parse into a dictionary.",
                "details": "The YAML content must represent a dictionary/object.",
            }

        # 2. 检查结构是否符合Pydantic模型
        protocol = ProtocolModel.model_validate(data)

        # 3. 额外验证：检查是否有重复的stage_name
        stage_names = [stage.stage_name for stage in protocol.stages]
        if len(stage_names) != len(set(stage_names)):
            return {
                "success": False,
                "error": "Duplicate stage names found.",
                "details": f"Stage names must be unique. Found: {stage_names}",
            }

        # 4. 依赖关系校验
        # 4.1 depends_on引用检查
        for stage in protocol.stages:
            if stage.depends_on:
                for dep in stage.depends_on:
                    if dep not in stage_names:
                        return {
                            "success": False,
                            "error": f"Stage '{stage.stage_name}' depends on undefined stage '{dep}'",
                            "details": "All depends_on must reference valid stage_name.",
                        }

        # 4.2 DAG环路检查
        def has_cycle(stages):
            graph = {s.stage_name: s.depends_on or [] for s in stages}
            visited = set()
            stack = set()

            def visit(node):
                if node in stack:
                    return True
                if node in visited:
                    return False
                stack.add(node)
                for neighbor in graph.get(node, []):
                    if visit(neighbor):
                        return True
                stack.remove(node)
                visited.add(node)
                return False

            return any(visit(n) for n in graph)

        if has_cycle(protocol.stages):
            return {
                "success": False,
                "error": "Stage dependency graph has a cycle.",
                "details": "Check depends_on fields for circular dependencies.",
            }
        # 4.3 inputs引用检查
        for stage in protocol.stages:
            if stage.inputs:
                for inp in stage.inputs:
                    if inp.type == "stage":
                        if not inp.from_stage or inp.from_stage not in stage_names:
                            return {
                                "success": False,
                                "error": f"Stage '{stage.stage_name}' input from_stage '{inp.from_stage}' not found.",
                                "details": "All stage-type inputs must reference valid from_stage.",
                            }
        # 4.4 outputs非空检查
        for stage in protocol.stages:
            if (
                not stage.outputs
                or not isinstance(stage.outputs, list)
                or not stage.outputs
            ):
                return {
                    "success": False,
                    "error": f"Stage '{stage.stage_name}' outputs field is missing or empty.",
                    "details": "Each stage must define at least one output key.",
                }

        return {
            "success": True,
            "message": "Protocol is valid.",
            "protocol_info": {
                "workflow_id": protocol.workflow_id,
                "description": protocol.description,
                "stage_count": len(protocol.stages),
                "stage_names": stage_names,
            },
        }

    except yaml.YAMLError as e:
        return {
            "success": False,
            "error": f"YAML Syntax Error: {e!s}",
            "details": "The YAML content contains syntax errors.",
        }
    except ValidationError as e:
        # 格式化Pydantic验证错误
        error_details = []
        for error in e.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            error_details.append(f"{field_path}: {error['msg']}")

        return {
            "success": False,
            "error": f"Schema Validation Error: {len(error_details)} validation errors found",
            "details": "\n".join(error_details),
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e!s}",
            "details": "An unexpected error occurred during validation.",
        }


def format_protocol_validation_result(result: dict[str, Any]) -> str:
    """格式化验证结果为人类可读的字符串

    Args:
    ----
        result: validate_protocol函数的返回结果

    Returns:
    -------
        格式化的字符串

    """
    if result["success"]:
        info = result.get("protocol_info", {})
        return (
            f"✅ Protocol validation successful!\n"
            f"   Workflow ID: {info.get('workflow_id', 'N/A')}\n"
            f"   Description: {info.get('description', 'N/A')}\n"
            f"   Stages: {info.get('stage_count', 0)} stages\n"
            f"   Stage names: {', '.join(info.get('stage_names', []))}"
        )
    else:
        return (
            f"❌ Protocol validation failed!\n"
            f"   Error: {result.get('error', 'Unknown error')}\n"
            f"   Details: {result.get('details', 'No details provided')}"
        )


# 测试函数
if __name__ == "__main__":
    # 测试有效的协议
    valid_yaml = """
workflow_id: test_protocol_v1
description: A test protocol for validation
stages:
  - stage_name: EXTRACT_DATA
    role: "数据提取专家"
    prompt_template: "Please extract data from: {document_text}"
    output_schema: "src.schemas.test.TestData"
  - stage_name: PROCESS_DATA
    role: "数据处理专家"
    prompt_template: "Process the extracted data: {extracted_data_json}"
    output_schema: "src.schemas.test.ProcessedData"
"""

    result = validate_protocol(valid_yaml)
    print("Valid protocol test:")
    print(format_protocol_validation_result(result))
    print()

    # 测试无效的协议
    invalid_yaml = """
workflow_id: invalid-protocol
description: An invalid protocol
stages:
  - stage_name: invalid stage name
    role: "测试角色"
    prompt_template: "测试模板"
    output_schema: "invalid.schema.path"
"""

    result = validate_protocol(invalid_yaml)
    print("Invalid protocol test:")
    print(format_protocol_validation_result(result))
