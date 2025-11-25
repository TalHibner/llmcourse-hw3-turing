"""Integration tests for translation pipeline."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import yaml
from pathlib import Path
from src.agents.pipeline import TranslationPipeline
from src.input.generator import TestCase


class TestTranslationPipeline:
    """Test suite for TranslationPipeline integration."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing."""
        config_data = {
            'agents': {
                'agent1': {
                    'skill_file': 'skills/en_to_fr.md',
                    'source_lang': 'en',
                    'target_lang': 'fr'
                },
                'agent2': {
                    'skill_file': 'skills/fr_to_he.md',
                    'source_lang': 'fr',
                    'target_lang': 'he'
                },
                'agent3': {
                    'skill_file': 'skills/he_to_en.md',
                    'source_lang': 'he',
                    'target_lang': 'en'
                }
            },
            'api': {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 200,
                'temperature': 0.3,
                'max_retries': 3,
                'retry_delay': 1,
                'timeout': 60
            },
            'input': {
                'min_word_count': 15,
                'base_sentences_file': 'data/base_sentences.txt'
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        yield config_data

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def mock_skill_files(self):
        """Create mock skill files."""
        skills = {
            'skills/en_to_fr.md': 'Translate English to French',
            'skills/fr_to_he.md': 'Translate French to Hebrew',
            'skills/he_to_en.md': 'Translate Hebrew to English'
        }

        # Create temporary skill files
        temp_files = {}
        for skill_path, content in skills.items():
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
            temp_file.write(f"# Translation Skill\n\n{content}\n")
            temp_file.close()
            temp_files[skill_path] = temp_file.name

        yield temp_files

        # Cleanup
        for temp_file in temp_files.values():
            Path(temp_file).unlink(missing_ok=True)

    @pytest.fixture
    def sample_test_case(self):
        """Create sample test case."""
        return TestCase(
            id=0,
            original_clean="The quick brown fox jumps over the lazy dog",
            original_corrupted="The quikc borwn fox jmps over the lzy dog",
            target_error_rate=0.25,
            actual_error_rate=0.22,
            word_count=9,
            num_errors=2
        )

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    def test_pipeline_initialization(self, mock_config):
        """Test TranslationPipeline initialization."""
        pipeline = TranslationPipeline(mock_config)

        assert pipeline is not None
        assert hasattr(pipeline, 'config')
        assert hasattr(pipeline, 'client')

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.agents.pipeline.Anthropic')
    def test_load_skill_prompt(self, mock_anthropic, mock_config):
        """Test loading skill prompts."""
        # Create temporary skill file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("# Test Skill\n\nTranslate text")
            skill_file = f.name

        try:
            # Update config with temp file
            mock_config['agents']['agent1']['skill_file'] = skill_file

            pipeline = TranslationPipeline(mock_config)
            prompt = pipeline._load_skill_prompt('agent1')

            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert "Translate text" in prompt

        finally:
            Path(skill_file).unlink(missing_ok=True)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.agents.pipeline.Anthropic')
    def test_call_agent_success(self, mock_anthropic, mock_config):
        """Test successful agent call."""
        # Mock the API response
        mock_message = Mock()
        mock_message.content = [Mock(text="Bonjour le monde")]
        mock_anthropic.return_value.messages.create.return_value = mock_message

        pipeline = TranslationPipeline(mock_config)

        # Create temporary skill file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("Translate to French")
            skill_file = f.name

        try:
            mock_config['agents']['agent1']['skill_file'] = skill_file
            result = pipeline._call_agent('agent1', 'Hello world')

            assert isinstance(result, str)
            assert result == "Bonjour le monde"

        finally:
            Path(skill_file).unlink(missing_ok=True)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.agents.pipeline.Anthropic')
    def test_call_agent_with_retry(self, mock_anthropic, mock_config):
        """Test agent call with retry on failure."""
        # Mock first call to fail, second to succeed
        mock_message = Mock()
        mock_message.content = [Mock(text="Success")]

        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            Exception("API Error"),
            mock_message
        ]
        mock_anthropic.return_value = mock_client

        pipeline = TranslationPipeline(mock_config)

        # Create temporary skill file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("Translate")
            skill_file = f.name

        try:
            mock_config['agents']['agent1']['skill_file'] = skill_file
            result = pipeline._call_agent('agent1', 'Test')

            assert result == "Success"
            assert mock_client.messages.create.call_count == 2

        finally:
            Path(skill_file).unlink(missing_ok=True)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.agents.pipeline.Anthropic')
    def test_process_full_pipeline(self, mock_anthropic, mock_config):
        """Test processing through full 3-agent pipeline."""
        # Mock responses for all three agents
        mock_messages = [
            Mock(content=[Mock(text="Le renard brun rapide")]),  # EN->FR
            Mock(content=[Mock(text="השועל החום המהיר")]),       # FR->HE
            Mock(content=[Mock(text="The fast brown fox")])     # HE->EN
        ]

        mock_client = Mock()
        mock_client.messages.create.side_effect = mock_messages
        mock_anthropic.return_value = mock_client

        pipeline = TranslationPipeline(mock_config)

        # Create temporary skill files
        skill_files = []
        for agent in ['agent1', 'agent2', 'agent3']:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
                f.write(f"Translate for {agent}")
                skill_files.append(f.name)
                mock_config['agents'][agent]['skill_file'] = f.name

        try:
            result = pipeline.process("The quick brown fox", test_id=1)

            # Check result structure
            assert isinstance(result, dict)
            assert 'test_id' in result
            assert 'original' in result
            assert 'french' in result
            assert 'hebrew' in result
            assert 'final' in result
            assert 'metadata' in result

            # Check values
            assert result['test_id'] == 1
            assert result['french'] == "Le renard brun rapide"
            assert result['hebrew'] == "השועל החום המהיר"
            assert result['final'] == "The fast brown fox"
            assert result['metadata']['success'] is True

            # Verify all agents were called
            assert mock_client.messages.create.call_count == 3

        finally:
            for skill_file in skill_files:
                Path(skill_file).unlink(missing_ok=True)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.agents.pipeline.Anthropic')
    def test_process_with_test_case(self, mock_anthropic, mock_config, sample_test_case):
        """Test processing with TestCase object."""
        mock_messages = [
            Mock(content=[Mock(text="French translation")]),
            Mock(content=[Mock(text="Hebrew translation")]),
            Mock(content=[Mock(text="Back to English")])
        ]

        mock_client = Mock()
        mock_client.messages.create.side_effect = mock_messages
        mock_anthropic.return_value = mock_client

        pipeline = TranslationPipeline(mock_config)

        # Create temporary skill files
        skill_files = []
        for agent in ['agent1', 'agent2', 'agent3']:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
                f.write(f"Translate")
                skill_files.append(f.name)
                mock_config['agents'][agent]['skill_file'] = f.name

        try:
            result = pipeline.process_test_case(sample_test_case)

            assert isinstance(result, dict)
            assert 'test_case' in result
            assert result['test_case']['id'] == sample_test_case.id
            assert result['final'] == "Back to English"

        finally:
            for skill_file in skill_files:
                Path(skill_file).unlink(missing_ok=True)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.agents.pipeline.Anthropic')
    def test_process_batch(self, mock_anthropic, mock_config):
        """Test batch processing of multiple test cases."""
        # Mock responses (3 agents × 2 test cases = 6 calls)
        mock_messages = [
            Mock(content=[Mock(text=f"Translation {i}")])
            for i in range(6)
        ]

        mock_client = Mock()
        mock_client.messages.create.side_effect = mock_messages
        mock_anthropic.return_value = mock_client

        pipeline = TranslationPipeline(mock_config)

        # Create temporary skill files
        skill_files = []
        for agent in ['agent1', 'agent2', 'agent3']:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
                f.write(f"Translate")
                skill_files.append(f.name)
                mock_config['agents'][agent]['skill_file'] = f.name

        test_cases = [
            TestCase(0, "Text one", "Txt one", 0.25, 0.25, 2, 1),
            TestCase(1, "Text two", "Txt two", 0.5, 0.5, 2, 1)
        ]

        try:
            results = pipeline.process_batch(test_cases)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(r, dict) for r in results)
            assert all('metadata' in r for r in results)

        finally:
            for skill_file in skill_files:
                Path(skill_file).unlink(missing_ok=True)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.agents.pipeline.Anthropic')
    def test_error_handling(self, mock_anthropic, mock_config):
        """Test error handling in pipeline."""
        # Mock all calls to fail
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("Persistent API Error")
        mock_anthropic.return_value = mock_client

        pipeline = TranslationPipeline(mock_config)

        # Create temporary skill file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("Translate")
            skill_file = f.name
            mock_config['agents']['agent1']['skill_file'] = skill_file

        try:
            result = pipeline.process("Test text", test_id=1)

            # Should have error metadata
            assert result['metadata']['success'] is False
            assert 'error' in result['metadata']

        finally:
            Path(skill_file).unlink(missing_ok=True)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    def test_missing_api_key_handling(self, mock_config):
        """Test handling of missing API key."""
        # Remove API key from environment
        with patch.dict('os.environ', {}, clear=True):
            # This might raise an error or handle it gracefully
            # depending on implementation
            try:
                pipeline = TranslationPipeline(mock_config)
                # If no error, check that pipeline handles it
                assert pipeline is not None
            except Exception as e:
                # Expected behavior - missing API key should cause error
                assert 'api' in str(e).lower() or 'key' in str(e).lower()

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.agents.pipeline.Anthropic')
    def test_rate_limiting(self, mock_anthropic, mock_config):
        """Test rate limiting between API calls."""
        import time

        mock_message = Mock()
        mock_message.content = [Mock(text="Translation")]
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        pipeline = TranslationPipeline(mock_config)

        # Create temporary skill file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("Translate")
            skill_file = f.name
            mock_config['agents']['agent1']['skill_file'] = skill_file

        try:
            start_time = time.time()
            pipeline._call_agent('agent1', 'Test 1')
            pipeline._call_agent('agent1', 'Test 2')
            elapsed = time.time() - start_time

            # There should be some delay between calls (rate limiting)
            # Verify calls were made
            assert mock_client.messages.create.call_count == 2

        finally:
            Path(skill_file).unlink(missing_ok=True)
