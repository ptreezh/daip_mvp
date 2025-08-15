"""@Time: 2025-08-03
@Author: Claude Code
@File: test_v0_3_5_simple.py
@Description: Simplified test suite for V0.3.5 Critical Review Workflow components
"""

import asyncio

# Import the simplified components to test
import sys
import time

import pytest

sys.path.append('.')

from src.core_services.smart_reviewer_allocator_simple import SmartReviewerAllocator


class TestSmartReviewerAllocator:
    """Test suite for SmartReviewerAllocator"""
    
    @pytest.fixture()
    def allocator(self):
        return SmartReviewerAllocator()
    
    @pytest.mark.asyncio()
    async def test_allocator_initialization(self, allocator):
        """Test allocator initialization"""
        assert allocator is not None
        assert hasattr(allocator, 'reviewer_pool')
        assert hasattr(allocator, 'allocation_history')
        assert len(allocator.reviewer_pool) > 0
    
    @pytest.mark.asyncio()
    async def test_select_reviewers_basic(self, allocator):
        """Test basic reviewer selection"""
        result = await allocator.select_reviewers(
            content_type='code_review',
            content_tags=['python', 'testing'],
            required_count=1
        )
        
        assert result['success'] is True
        assert len(result['selected_reviewers']) == 1
        assert 'allocation_id' in result
        assert 'scores' in result
        assert result['confidence_score'] > 0.0
    
    @pytest.mark.asyncio()
    async def test_select_reviewers_multiple(self, allocator):
        """Test selecting multiple reviewers"""
        result = await allocator.select_reviewers(
            content_type='code_review',
            content_tags=['python', 'testing'],
            required_count=3
        )
        
        assert result['success'] is True
        assert len(result['selected_reviewers']) <= 3
        assert len(result['selected_reviewers']) > 0
    
    @pytest.mark.asyncio()
    async def test_select_reviewers_no_available(self, allocator):
        """Test reviewer selection when no reviewers available"""
        # Clear reviewer pool
        allocator.reviewer_pool = {}
        
        result = await allocator.select_reviewers(
            content_type='code_review',
            content_tags=['python'],
            required_count=1
        )
        
        assert result['success'] is False
        assert 'No available reviewers' in result['error']
    
    @pytest.mark.asyncio()
    async def test_calculate_match_score(self, allocator):
        """Test match score calculation"""
        reviewer = {
            'expertise': ['python', 'testing'],
            'workload': 0.3
        }
        
        score = allocator._calculate_match_score(
            reviewer, 
            ['python', 'testing'], 
            'code_review'
        )
        
        assert 0 <= score <= 1
        assert score > 0.5  # Should be a good match
    
    @pytest.mark.asyncio()
    async def test_pool_stats(self, allocator):
        """Test pool statistics"""
        stats = allocator.get_pool_stats()
        
        assert isinstance(stats, dict)
        assert 'total_reviewers' in stats
        assert 'available_reviewers' in stats
        assert 'average_workload' in stats
        assert 'specialization_distribution' in stats
        
        assert stats['total_reviewers'] > 0
        assert stats['available_reviewers'] >= 0
        assert stats['average_workload'] >= 0


class TestV0_3_5BasicIntegration:
    """Basic integration tests for V0.3.5 components"""
    
    @pytest.mark.asyncio()
    async def test_allocator_workflow(self):
        """Test complete allocator workflow"""
        # Initialize allocator
        allocator = SmartReviewerAllocator()
        
        # Test different content types
        test_cases = [
            {
                'content_type': 'code_review',
                'content_tags': ['python', 'testing'],
                'required_count': 2
            },
            {
                'content_type': 'research_paper',
                'content_tags': ['AI', 'machine learning'],
                'required_count': 3
            },
            {
                'content_type': 'design_review',
                'content_tags': ['UI', 'UX'],
                'required_count': 1
            }
        ]
        
        for test_case in test_cases:
            result = await allocator.select_reviewers(**test_case)
            
            assert result['success'] is True
            assert len(result['selected_reviewers']) <= test_case['required_count']
            assert result['confidence_score'] > 0.0
            
            # Verify reviewers exist in pool
            for reviewer_id in result['selected_reviewers']:
                assert reviewer_id in allocator.reviewer_pool
    
    @pytest.mark.asyncio()
    async def test_allocator_performance(self):
        """Test allocator performance"""
        allocator = SmartReviewerAllocator()
        
        start_time = time.time()
        
        # Run multiple allocation requests
        tasks = []
        for i in range(10):
            task = allocator.select_reviewers(
                content_type=f'content_type_{i}',
                content_tags=['tag1', 'tag2'],
                required_count=2
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        # Verify all requests succeeded
        assert all(result['success'] for result in results)
        
        # Performance check (should complete within 5 seconds)
        assert (end_time - start_time) < 5.0
        
        print(f"Performance test completed in {end_time - start_time:.2f} seconds")
    
    @pytest.mark.asyncio()
    async def test_error_handling(self):
        """Test error handling"""
        allocator = SmartReviewerAllocator()
        
        # Test with invalid parameters
        result = await allocator.select_reviewers(
            content_type='',
            content_tags=[],
            required_count=0
        )
        
        # Should handle gracefully
        assert 'success' in result
        assert 'error' in result or result['success'] is True


@pytest.mark.asyncio()
async def test_comprehensive_validation():
    """Comprehensive validation test"""
    allocator = SmartReviewerAllocator()
    
    # Test 1: Basic functionality
    result1 = await allocator.select_reviewers(
        content_type='code_review',
        content_tags=['python'],
        required_count=1
    )
    assert result1['success'] is True
    
    # Test 2: Multiple reviewers
    result2 = await allocator.select_reviewers(
        content_type='research_paper',
        content_tags=['AI', 'ML'],
        required_count=3
    )
    assert result2['success'] is True
    
    # Test 3: Pool statistics
    stats = allocator.get_pool_stats()
    assert stats['total_reviewers'] > 0
    
    # Test 4: Edge case - more reviewers than available
    result3 = await allocator.select_reviewers(
        content_type='code_review',
        content_tags=['python'],
        required_count=10
    )
    assert result3['success'] is True
    assert len(result3['selected_reviewers']) <= stats['total_reviewers']
    
    print("Comprehensive validation passed!")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])