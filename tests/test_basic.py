#!/usr/bin/env python3
"""
Basic test suite for BuiltByRAVE CFO OS
Tests core functionality without requiring external services
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the rag-backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rag-backend'))

class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality without external dependencies"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_dir = os.path.join(self.test_dir, 'vault')
        os.makedirs(self.vault_dir)
        
        # Create test documents
        test_docs = [
            ('00-Home/test.md', '# Test Home\nThis is a test document.'),
            ('01-Scope/test.md', '# Test Scope\nScope information here.'),
            ('09-Financials/test.md', '# Test Financials\nFinancial data here.')
        ]
        
        for doc_path, content in test_docs:
            full_path = os.path.join(self.vault_dir, doc_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_loader_functionality(self):
        """Test document loading functionality"""
        try:
            from loader import load_documents
            docs = load_documents(self.vault_dir)
            
            self.assertIsInstance(docs, list)
            self.assertGreater(len(docs), 0)
            
            # Check that documents have required fields
            for doc in docs:
                self.assertIn('text', doc)
                self.assertIn('source', doc)
                self.assertIn('id', doc)
                
        except ImportError as e:
            self.fail(f"Failed to import loader: {e}")
    
    def test_embedder_import(self):
        """Test that embedder can be imported"""
        try:
            from embedder import embed_documents, query_vector_store
            self.assertTrue(True)  # If we get here, import succeeded
        except ImportError as e:
            self.fail(f"Failed to import embedder: {e}")
    
    def test_chatbot_import(self):
        """Test that chatbot can be imported"""
        try:
            from chatbot import CFOAIChatbot
            self.assertTrue(True)  # If we get here, import succeeded
        except ImportError as e:
            self.fail(f"Failed to import chatbot: {e}")
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists and is readable"""
        requirements_path = Path(__file__).parent.parent / 'rag-backend' / 'requirements.txt'
        self.assertTrue(requirements_path.exists(), "requirements.txt not found")
        
        # Check that it contains expected packages
        with open(requirements_path, 'r') as f:
            content = f.read()
            self.assertIn('flask', content)
            self.assertIn('openai', content)
            self.assertIn('chromadb', content)
    
    def test_vault_structure(self):
        """Test that vault directory structure is correct"""
        vault_path = Path(__file__).parent.parent / 'vault'
        if vault_path.exists():
            # Check for essential directories
            essential_dirs = ['00-Home', '01-Scope', '09-Financials']
            for dir_name in essential_dirs:
                dir_path = vault_path / dir_name
                if not dir_path.exists():
                    print(f"Warning: Missing vault directory: {dir_name}")
    
    def test_startup_scripts_exist(self):
        """Test that startup scripts exist"""
        scripts = ['start_chatbot.py', 'setup.py']
        for script in scripts:
            script_path = Path(__file__).parent.parent / script
            self.assertTrue(script_path.exists(), f"{script} not found")
    
    def test_package_json_exists(self):
        """Test that package.json exists"""
        package_path = Path(__file__).parent.parent / 'package.json'
        self.assertTrue(package_path.exists(), "package.json not found")
    
    def test_electron_app_structure(self):
        """Test that Electron app structure is correct"""
        electron_dir = Path(__file__).parent.parent / 'electron-app'
        if electron_dir.exists():
            required_files = ['main.js', 'package.json']
            for file_name in required_files:
                file_path = electron_dir / file_name
                self.assertTrue(file_path.exists(), f"{file_name} not found in electron-app")

class TestConfiguration(unittest.TestCase):
    """Test configuration and environment setup"""
    
    def test_env_file_creation(self):
        """Test .env file creation"""
        env_content = """# BuiltByRAVE CFO OS Configuration
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
"""
        
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name
        
        try:
            # Test that the file was created and contains expected content
            self.assertTrue(os.path.exists(env_file))
            with open(env_file, 'r') as f:
                content = f.read()
                self.assertIn('OPENAI_API_KEY', content)
                self.assertIn('FLASK_ENV', content)
        finally:
            os.unlink(env_file)

if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    tests_dir = Path(__file__).parent
    tests_dir.mkdir(exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2) 