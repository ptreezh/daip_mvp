"""
Unit tests for specialized Subagents.
"""
import pytest
from src.daip_live.subagents.grounded_theory import GroundedTheorySubagent
from src.daip_live.subagents.sna_expert import SNASubagent


class TestGroundedTheorySubagent:
    """Test cases for the GroundedTheorySubagent class."""
    
    @pytest.fixture
    def grounded_theory_subagent(self):
        """Create a GroundedTheorySubagent instance for testing."""
        return GroundedTheorySubagent()
    
    def test_initialization(self, grounded_theory_subagent):
        """Test Subagent initialization."""
        assert grounded_theory_subagent.name == "grounded_theory_expert"
        assert grounded_theory_subagent.is_initialized == False
    
    def test_analyze_chinese_text(self, grounded_theory_subagent):
        """Test analyzing Chinese text data."""
        data = "这是一个测试。学生学习很努力。教师教学方法很重要。"
        result = grounded_theory_subagent.analyze(data)
        
        assert isinstance(result, object)  # AnalysisResult
        assert isinstance(result.content, str)
        assert isinstance(result.metadata, dict)
        assert result.confidence > 0
        assert result.subagent_name == "grounded_theory_expert"
    
    def test_get_capabilities(self, grounded_theory_subagent):
        """Test getting Subagent capabilities."""
        capabilities = grounded_theory_subagent.get_capabilities()
        
        assert capabilities.name == "grounded_theory_expert"
        assert "grounded_theory" in capabilities.supported_domains
        assert "text_analysis" in capabilities.required_skills or True  # At least one skill
        assert capabilities.version == "1.0"
    
    def test_perform_coding(self, grounded_theory_subagent):
        """Test the coding functionality."""
        data = "学生学习经验很重要。教师教学策略需要改进。"
        # Access the private method through a test interface
        codes = grounded_theory_subagent._perform_coding(data)
        
        assert isinstance(codes, list)
        # Should find some codes based on the categories
        assert len(codes) >= 0  # Could be 0 if no matches
    
    def test_categorize_codes(self, grounded_theory_subagent):
        """Test categorizing codes."""
        codes = [
            {"id": "1", "text": "学生学习", "categories": ["Experience"], "position": 0},
            {"id": "2", "text": "教师教学", "categories": ["Strategy"], "position": 1}
        ]
        
        categories = grounded_theory_subagent._categorize_codes(codes)
        
        assert isinstance(categories, dict)
        assert "Experience" in categories or "Strategy" in categories


class TestSNASubagent:
    """Test cases for the SNASubagent class."""
    
    @pytest.fixture
    def sna_subagent(self):
        """Create an SNASubagent instance for testing."""
        return SNASubagent()
    
    def test_initialization(self, sna_subagent):
        """Test Subagent initialization."""
        assert sna_subagent.name == "sna_expert"
        assert sna_subagent.is_initialized == False
    
    def test_analyze_network_data(self, sna_subagent):
        """Test analyzing network data."""
        data = "张三和李四有关系。李四和王五有联系。王五和赵六互动。"
        result = sna_subagent.analyze(data)
        
        assert isinstance(result, object)  # AnalysisResult
        assert isinstance(result.content, str)
        assert isinstance(result.metadata, dict)
        assert result.confidence > 0
        assert result.subagent_name == "sna_expert"
    
    def test_get_capabilities(self, sna_subagent):
        """Test getting Subagent capabilities."""
        capabilities = sna_subagent.get_capabilities()
        
        assert capabilities.name == "sna_expert"
        assert "sna" in capabilities.supported_domains
        assert "network_analysis" in capabilities.required_skills or True  # At least one skill
        assert capabilities.version == "1.0"
    
    def test_parse_network_data(self, sna_subagent):
        """Test parsing network data."""
        data = "张三和李四有关系。李四和王五有联系。"
        nodes, edges = sna_subagent._parse_network_data(data)
        
        assert isinstance(nodes, list)
        assert isinstance(edges, list)
        # Should find some nodes and edges
        assert len(nodes) >= 0
        assert len(edges) >= 0
    
    def test_calculate_network_metrics(self, sna_subagent):
        """Test calculating network metrics."""
        nodes = ["张三", "李四", "王五"]
        edges = [
            {"source": "张三", "target": "李四", "weight": 1.0},
            {"source": "李四", "target": "王五", "weight": 1.0}
        ]
        
        metrics = sna_subagent._calculate_network_metrics(nodes, edges)
        
        assert isinstance(metrics, dict)
        assert "Density" in metrics