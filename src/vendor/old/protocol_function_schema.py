protocol_step_extraction_schema = {
    "name": "extract_protocol_steps",
    "description": "从自然语言协议描述中提取结构化步骤和节点",
    "parameters": {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "步骤名称"},
                        "role": {"type": "string", "description": "责任角色"},
                        "type": {
                            "type": "string",
                            "enum": ["user_input", "auto", "approval"],
                            "description": "节点类型",
                        },
                        "next": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "后续步骤名称",
                        },
                    },
                    "required": ["name"],
                },
            },
        },
        "required": ["steps"],
    },
}
