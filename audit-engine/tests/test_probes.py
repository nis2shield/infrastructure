#!/usr/bin/env python3
"""
Unit tests for the NIS2 Compliance Engine probes.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from probes.trivy_scanner import analyze_results, TrivyResult
from probes.log_analyzer import LogAnalysisResult, check_backup_artifacts


class TestTrivyScanner(unittest.TestCase):
    """Tests for Probe B: Trivy Scanner."""
    
    def test_analyze_empty_results(self):
        """No vulnerabilities should return PASS."""
        trivy_output = {"Results": []}
        result = analyze_results(trivy_output)
        
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.critical_count, 0)
        self.assertEqual(result.high_count, 0)
        self.assertIn("No CRITICAL/HIGH", result.evidence)
    
    def test_analyze_critical_vulnerabilities(self):
        """CRITICAL CVEs should return FAIL."""
        trivy_output = {
            "Results": [{
                "Vulnerabilities": [
                    {"Severity": "CRITICAL", "PkgName": "openssl"},
                    {"Severity": "CRITICAL", "PkgName": "libcrypto"},
                    {"Severity": "HIGH", "PkgName": "requests"}
                ]
            }]
        }
        result = analyze_results(trivy_output)
        
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.critical_count, 2)
        self.assertEqual(result.high_count, 1)
        self.assertIn("openssl", result.evidence)
    
    def test_analyze_high_only(self):
        """HIGH CVEs without CRITICAL should return WARN."""
        trivy_output = {
            "Results": [{
                "Vulnerabilities": [
                    {"Severity": "HIGH", "PkgName": "django"},
                    {"Severity": "MEDIUM", "PkgName": "flask"}
                ]
            }]
        }
        result = analyze_results(trivy_output)
        
        self.assertEqual(result.status, "WARN")
        self.assertEqual(result.critical_count, 0)
        self.assertEqual(result.high_count, 1)
    
    def test_nis2_article_mapping(self):
        """Results should map to NIS2 Art. 21.2.d."""
        result = analyze_results({"Results": []})
        self.assertEqual(result.nis2_article, "21.2.d")


class TestLogAnalyzer(unittest.TestCase):
    """Tests for Probe D: Log Analyzer."""
    
    def test_check_backup_missing_directory(self):
        """Non-existent backup dir should return WARN."""
        result = check_backup_artifacts("/nonexistent/path")
        
        self.assertEqual(result.status, "WARN")
        self.assertIn("not found", result.evidence)
    
    def test_check_backup_with_files(self):
        """Recent backup files should return PASS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a recent backup file
            backup_file = os.path.join(tmpdir, "backup_2024.sql.gz")
            with open(backup_file, 'w') as f:
                f.write("backup data")
            
            result = check_backup_artifacts(tmpdir)
            
            self.assertEqual(result.status, "PASS")
            self.assertIn("backup_2024.sql.gz", result.evidence)
    
    def test_check_backup_empty_directory(self):
        """Empty backup directory should return FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_backup_artifacts(tmpdir)
            
            self.assertEqual(result.status, "FAIL")
            self.assertIn("No backups", result.evidence)
    
    def test_nis2_article_mapping(self):
        """Results should map to NIS2 Art. 21.2.c."""
        result = check_backup_artifacts("/nonexistent")
        self.assertEqual(result.nis2_article, "21.2.c")


class TestMarkdownUpdater(unittest.TestCase):
    """Tests for the markdown magic marker updater."""
    
    def setUp(self):
        from main import update_markdown
        self.update_markdown = update_markdown
    
    def test_update_status_marker(self):
        """Status markers should be updated correctly."""
        content = "| 21.2.c | Backup | <!--status-21.2.c-->❓ UNKNOWN<!--end--> |"
        updates = {"21.2.c": {"status": "PASS", "evidence": "Test"}}
        
        result = self.update_markdown(content, updates)
        
        self.assertIn("✅ PASS", result)
        self.assertNotIn("❓ UNKNOWN", result)
    
    def test_update_evidence_marker(self):
        """Evidence markers should be updated with date."""
        content = "| Evidence | <!--evidence-21.2.c-->Old evidence<!--end--> |"
        updates = {"21.2.c": {"status": "PASS", "evidence": "New evidence"}}
        
        result = self.update_markdown(content, updates)
        
        self.assertIn("New evidence", result)
        self.assertIn("Auto-checked:", result)
        self.assertNotIn("Old evidence", result)
    
    def test_preserves_non_marker_content(self):
        """Non-marker content should be preserved."""
        content = """# NIS2 Assessment
Some manual notes here.
<!--status-21.2.c-->FAIL<!--end-->
More notes."""
        updates = {"21.2.c": {"status": "PASS", "evidence": "Fixed"}}
        
        result = self.update_markdown(content, updates)
        
        self.assertIn("Some manual notes here", result)
        self.assertIn("More notes", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
