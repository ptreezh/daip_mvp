# CLI Usage Examples

This document provides examples of how to use the Virtual Role Chat System CLI interface.

## Installation and Setup

First, ensure you have the required dependencies installed:

```bash
pip install click rich fastapi uvicorn pydantic
```

## Basic Usage

### List Available Workflows

```bash
python -m src.user_interface.cli list-workflows
```

### Get Help for a Specific Workflow

```bash
python -m src.user_interface.cli help-workflow critical-review
python -m src.user_interface.cli help-workflow multi-perspective
```

## Critical Review Workflow

### Basic Usage

```bash
python -m src.user_interface.cli critical-review --content "人工智能将在2025年完全替代人类工作。这是基于最新的研究报告得出的结论。"
```

### Using a File as Input

```bash
python -m src.user_interface.cli critical-review --content-file examples/sample_content.txt
```

### Using Custom Configuration

```bash
python -m src.user_interface.cli critical-review \
  --content "AI技术正在快速发展，预计将对各行各业产生深远影响。" \
  --config-file examples/config/critical_review_config.json \
  --format rich
```

### Saving Results to File

```bash
python -m src.user_interface.cli critical-review \
  --content "量子计算将在未来十年内实现商业化应用。" \
  --output-file results/critical_review_result.json \
  --format json
```

### Markdown Output

```bash
python -m src.user_interface.cli critical-review \
  --content "区块链技术将彻底改变金融行业。" \
  --format markdown \
  --output-file results/review_report.md
```

## Multi-perspective Synthesis Workflow

### Basic Usage

```bash
python -m src.user_interface.cli multi-perspective --topic "人工智能对未来教育的影响"
```

### Specifying Custom Perspectives

```bash
python -m src.user_interface.cli multi-perspective \
  --topic "气候变化的应对策略" \
  --perspectives "环境,经济,政治,技术,社会"
```

### Using Custom Configuration

```bash
python -m src.user_interface.cli multi-perspective \
  --topic "数字货币的未来发展" \
  --config-file examples/config/multi_perspective_config.json \
  --format rich
```

### Comprehensive Analysis with Output

```bash
python -m src.user_interface.cli multi-perspective \
  --topic "可持续发展目标的实现路径" \
  --perspectives "经济,环境,社会,技术,政治,伦理" \
  --output-file results/sustainability_analysis.md \
  --format markdown \
  --verbose
```

## Advanced Usage

### Verbose Mode for Debugging

```bash
python -m src.user_interface.cli --verbose critical-review \
  --content "5G技术将带来安全风险。" \
  --format json
```

### Combining Multiple Operations

You can run multiple analyses and compare results:

```bash
# First analysis
python -m src.user_interface.cli multi-perspective \
  --topic "远程工作的影响" \
  --perspectives "经济,社会,技术" \
  --output-file results/remote_work_basic.json \
  --format json

# Second analysis with more perspectives
python -m src.user_interface.cli multi-perspective \
  --topic "远程工作的影响" \
  --perspectives "经济,社会,技术,心理,管理,法律" \
  --output-file results/remote_work_comprehensive.json \
  --format json
```

## Output Formats

### Rich Format (Default)
- Colorful, formatted output in the terminal
- Tables, panels, and progress bars
- Best for interactive use

### JSON Format
- Machine-readable structured data
- Includes all workflow details and metadata
- Best for programmatic processing

### Markdown Format
- Human-readable formatted text
- Suitable for documentation and reports
- Can be easily converted to other formats

## Configuration Files

### Critical Review Configuration

Create a JSON file with custom settings:

```json
{
  "generation": {
    "role_name": "专业分析师"
  },
  "consensus": {
    "credibility_threshold": 0.8
  },
  "revision": {
    "max_revision_attempts": 2
  }
}
```

### Multi-perspective Configuration

```json
{
  "task_decomposition": {
    "max_sub_problems": 5
  },
  "enhanced_synthesis": {
    "quality_threshold": 0.85
  },
  "iterative_refinement": {
    "max_iterations": 2
  }
}
```

## Error Handling

If a workflow fails, use the `--verbose` flag to get detailed error information:

```bash
python -m src.user_interface.cli --verbose multi-perspective \
  --topic "复杂主题" \
  --format json
```

## Tips and Best Practices

1. **Use appropriate perspectives**: Choose perspectives that are relevant to your topic
2. **Configure quality thresholds**: Adjust quality thresholds based on your needs
3. **Save important results**: Use `--output-file` to save results for later analysis
4. **Use verbose mode for debugging**: Enable verbose mode when troubleshooting issues
5. **Experiment with configurations**: Try different configurations to optimize results

## Integration with Other Tools

### Using with jq for JSON Processing

```bash
python -m src.user_interface.cli multi-perspective \
  --topic "AI伦理问题" \
  --format json | jq '.synthesis'
```

### Converting Markdown to PDF

```bash
python -m src.user_interface.cli multi-perspective \
  --topic "数字化转型" \
  --format markdown \
  --output-file report.md

pandoc report.md -o report.pdf
```

### Batch Processing

Create a script to process multiple topics:

```bash
#!/bin/bash
topics=("AI发展趋势" "绿色能源" "数字经济")

for topic in "${topics[@]}"; do
  python -m src.user_interface.cli multi-perspective \
    --topic "$topic" \
    --output-file "results/${topic// /_}.json" \
    --format json
done
```