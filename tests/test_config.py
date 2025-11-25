"""Unit tests for configuration management module."""

import pytest
import tempfile
import yaml
from pathlib import Path
from src.utils.config import load_config, get_config_value


class TestConfigLoader:
    """Test suite for configuration loading functions."""

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing."""
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
                }
            },
            'input': {
                'base_sentences_file': 'data/test_sentences.txt',
                'error_rates': [0.0, 0.25, 0.5]
            },
            'analysis': {
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
                'distance_metric': 'cosine'
            },
            'output': {
                'results_dir': 'results'
            },
            'api': {
                'model': 'claude-3-5-sonnet-20241022',
                'max_retries': 3,
                'timeout': 60
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    def test_load_config_success(self, temp_config_file):
        """Test successful config loading."""
        config = load_config(temp_config_file)

        assert isinstance(config, dict)
        assert 'agents' in config
        assert 'input' in config
        assert 'analysis' in config

    def test_load_config_nonexistent_file(self):
        """Test that loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_config('nonexistent_config.yaml')

    def test_load_config_structure(self, temp_config_file):
        """Test that loaded config has expected structure."""
        config = load_config(temp_config_file)

        # Check top-level keys
        assert 'agents' in config
        assert 'input' in config
        assert 'analysis' in config
        assert 'output' in config
        assert 'api' in config

    def test_load_config_agent_configuration(self, temp_config_file):
        """Test agent configuration structure."""
        config = load_config(temp_config_file)

        assert 'agent1' in config['agents']
        assert 'agent2' in config['agents']

        agent1 = config['agents']['agent1']
        assert 'skill_file' in agent1
        assert 'source_lang' in agent1
        assert 'target_lang' in agent1
        assert agent1['source_lang'] == 'en'
        assert agent1['target_lang'] == 'fr'

    def test_load_config_input_configuration(self, temp_config_file):
        """Test input configuration structure."""
        config = load_config(temp_config_file)

        input_config = config['input']
        assert 'base_sentences_file' in input_config
        assert 'error_rates' in input_config
        assert isinstance(input_config['error_rates'], list)

    def test_load_config_analysis_configuration(self, temp_config_file):
        """Test analysis configuration structure."""
        config = load_config(temp_config_file)

        analysis_config = config['analysis']
        assert 'embedding_model' in analysis_config
        assert 'distance_metric' in analysis_config
        assert analysis_config['distance_metric'] == 'cosine'

    def test_load_config_api_configuration(self, temp_config_file):
        """Test API configuration structure."""
        config = load_config(temp_config_file)

        api_config = config['api']
        assert 'model' in api_config
        assert 'max_retries' in api_config
        assert 'timeout' in api_config
        assert isinstance(api_config['max_retries'], int)

    def test_get_config_value_simple(self, temp_config_file):
        """Test getting simple config value."""
        config = load_config(temp_config_file)

        value = get_config_value(config, 'output', 'results_dir')
        assert value == 'results'

    def test_get_config_value_nested(self, temp_config_file):
        """Test getting nested config value."""
        config = load_config(temp_config_file)

        value = get_config_value(config, 'agents', 'agent1', 'source_lang')
        assert value == 'en'

    def test_get_config_value_with_default(self, temp_config_file):
        """Test getting config value with default."""
        config = load_config(temp_config_file)

        # Non-existent key should return default
        value = get_config_value(config, 'nonexistent', 'key', default='default_value')
        assert value == 'default_value'

    def test_get_config_value_no_default(self, temp_config_file):
        """Test getting non-existent value without default."""
        config = load_config(temp_config_file)

        value = get_config_value(config, 'nonexistent', 'key')
        assert value is None

    def test_get_config_value_partial_path(self, temp_config_file):
        """Test getting value with partial path."""
        config = load_config(temp_config_file)

        # Get entire 'agents' section
        value = get_config_value(config, 'agents')
        assert isinstance(value, dict)
        assert 'agent1' in value

    def test_get_config_value_deep_nesting(self, temp_config_file):
        """Test getting deeply nested value."""
        config = load_config(temp_config_file)

        value = get_config_value(config, 'agents', 'agent1', 'skill_file')
        assert value == 'skills/en_to_fr.md'

    def test_load_config_preserves_types(self, temp_config_file):
        """Test that config loading preserves data types."""
        config = load_config(temp_config_file)

        # List type
        error_rates = config['input']['error_rates']
        assert isinstance(error_rates, list)

        # Integer type
        max_retries = config['api']['max_retries']
        assert isinstance(max_retries, int)

        # String type
        model = config['api']['model']
        assert isinstance(model, str)

    def test_load_config_empty_file(self):
        """Test loading empty config file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write('')
            temp_path = f.name

        try:
            config = load_config(temp_path)
            # Empty YAML file returns None
            assert config is None or config == {}
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_config_malformed_yaml(self):
        """Test loading malformed YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write('invalid: yaml: content::: [[[')
            temp_path = f.name

        try:
            with pytest.raises(yaml.YAMLError):
                load_config(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_real_config_file(self):
        """Test loading the actual project config file."""
        config_path = 'config/config.yaml'

        # Only run if file exists
        if Path(config_path).exists():
            config = load_config(config_path)

            assert isinstance(config, dict)
            # Check for expected top-level keys
            expected_keys = ['agents', 'input', 'analysis', 'output', 'api']
            for key in expected_keys:
                assert key in config, f"Expected key '{key}' not found in config"

    def test_config_value_list_access(self, temp_config_file):
        """Test accessing list values from config."""
        config = load_config(temp_config_file)

        error_rates = get_config_value(config, 'input', 'error_rates')
        assert isinstance(error_rates, list)
        assert len(error_rates) == 3
        assert 0.0 in error_rates
        assert 0.25 in error_rates
        assert 0.5 in error_rates

    def test_config_modification(self, temp_config_file):
        """Test that config can be modified after loading."""
        config = load_config(temp_config_file)

        # Modify config
        config['api']['max_retries'] = 5

        assert config['api']['max_retries'] == 5

    def test_get_config_value_type_safety(self, temp_config_file):
        """Test type safety of get_config_value."""
        config = load_config(temp_config_file)

        # Try to access non-dict value as if it were nested
        value = get_config_value(config, 'api', 'max_retries', 'nested', default='default')
        # Should return default since max_retries is not a dict
        assert value == 'default'

    def test_config_unicode_handling(self):
        """Test handling of unicode characters in config."""
        config_data = {
            'test': {
                'french': 'Bonjour, ça va?',
                'hebrew': 'שלום עולם',
                'emoji': '🔥🎉'
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
            temp_path = f.name

        try:
            config = load_config(temp_path)
            assert config['test']['french'] == 'Bonjour, ça va?'
            assert config['test']['hebrew'] == 'שלום עולם'
            assert config['test']['emoji'] == '🔥🎉'
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_config_numeric_values(self):
        """Test handling of various numeric types."""
        config_data = {
            'numbers': {
                'integer': 42,
                'float': 3.14,
                'negative': -10,
                'zero': 0
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            config = load_config(temp_path)
            assert config['numbers']['integer'] == 42
            assert config['numbers']['float'] == 3.14
            assert config['numbers']['negative'] == -10
            assert config['numbers']['zero'] == 0
        finally:
            Path(temp_path).unlink(missing_ok=True)
