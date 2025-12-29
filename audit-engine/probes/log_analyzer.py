#!/usr/bin/env python3
"""
Probe D: Operational Log Analyzer (NIS2 Art. 21.2.c)
Verifies backup execution and DR tests via GitHub Actions API.
"""
import os
import json
import sys
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class LogAnalysisResult:
    """Result from operational log analysis."""
    status: str  # PASS, WARN, FAIL
    evidence: str
    last_run: Optional[str]
    nis2_article: str = "21.2.c"  # Business Continuity


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def check_workflow_runs(
    repo: str,
    workflow_name: str,
    days: int = 7,
    token: Optional[str] = None
) -> LogAnalysisResult:
    """
    Check if a GitHub Actions workflow ran successfully within the specified period.
    
    Args:
        repo: Repository in format 'owner/repo'
        workflow_name: Name of the workflow file (e.g., 'backup-test.yml')
        days: Number of days to look back
        token: GitHub token for API auth
    
    Returns:
        LogAnalysisResult with NIS2 compliance status
    """
    if not HAS_REQUESTS:
        return LogAnalysisResult(
            status="WARN",
            evidence="⚠️ 'requests' library not installed",
            last_run=None
        )
    
    token = token or get_github_token()
    if not token:
        return LogAnalysisResult(
            status="WARN",
            evidence="⚠️ GITHUB_TOKEN not set, cannot verify workflow runs",
            last_run=None
        )
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get workflow runs
        url = f"https://api.github.com/repos/{repo}/actions/runs"
        params = {
            "status": "success",
            "per_page": 50,
            "created": f">={datetime.now() - timedelta(days=days):%Y-%m-%d}"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        runs = response.json().get("workflow_runs", [])
        
        # Filter by workflow name
        matching_runs = [
            run for run in runs 
            if workflow_name.lower() in run.get("name", "").lower()
            or workflow_name.lower() in run.get("path", "").lower()
        ]
        
        if matching_runs:
            latest = matching_runs[0]
            last_run_date = latest.get("created_at", "")[:10]
            
            return LogAnalysisResult(
                status="PASS",
                evidence=f"✅ Workflow '{workflow_name}' ran on {last_run_date}",
                last_run=last_run_date
            )
        else:
            return LogAnalysisResult(
                status="WARN",
                evidence=f"⚠️ No successful runs of '{workflow_name}' in last {days} days",
                last_run=None
            )
            
    except requests.RequestException as e:
        return LogAnalysisResult(
            status="WARN",
            evidence=f"⚠️ Failed to query GitHub API: {str(e)[:50]}",
            last_run=None
        )


def check_backup_artifacts(backup_dir: str = "./backups") -> LogAnalysisResult:
    """
    Check if backup files exist and are recent.
    
    Args:
        backup_dir: Directory containing backup files
    
    Returns:
        LogAnalysisResult with NIS2 compliance status
    """
    if not os.path.exists(backup_dir):
        return LogAnalysisResult(
            status="WARN",
            evidence=f"⚠️ Backup directory '{backup_dir}' not found",
            last_run=None
        )
    
    backup_files = []
    now = datetime.now()
    
    for f in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, f)
        if os.path.isfile(filepath):
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            age_days = (now - mtime).days
            if age_days <= 7:  # Within last 7 days
                backup_files.append((f, mtime))
    
    if backup_files:
        latest = max(backup_files, key=lambda x: x[1])
        return LogAnalysisResult(
            status="PASS",
            evidence=f"✅ Recent backup: {latest[0]} ({latest[1]:%Y-%m-%d})",
            last_run=latest[1].isoformat()
        )
    else:
        return LogAnalysisResult(
            status="FAIL",
            evidence=f"❌ No backups found in last 7 days",
            last_run=None
        )


def analyze_operational_continuity(
    repo: str = "nis2shield/infrastructure",
    workflow_name: str = "backup",
    backup_dir: str = "./backups"
) -> dict:
    """
    Main entry point: Check operational continuity for NIS2 Art. 21.2.c.
    
    Returns:
        dict with NIS2 compliance status
    """
    # First check GitHub Actions
    gh_result = check_workflow_runs(repo, workflow_name)
    
    # If GitHub check passes, use that
    if gh_result.status == "PASS":
        return {
            "status": gh_result.status,
            "evidence": gh_result.evidence,
            "nis2_article": gh_result.nis2_article,
            "details": {
                "source": "github_actions",
                "last_run": gh_result.last_run
            }
        }
    
    # Fallback to local backup check
    local_result = check_backup_artifacts(backup_dir)
    
    return {
        "status": local_result.status,
        "evidence": local_result.evidence,
        "nis2_article": local_result.nis2_article,
        "details": {
            "source": "local_filesystem",
            "last_run": local_result.last_run,
            "github_status": gh_result.evidence
        }
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NIS2 Operational Log Analyzer (Probe D)")
    parser.add_argument("--repo", default="nis2shield/infrastructure", help="GitHub repo")
    parser.add_argument("--workflow", default="backup", help="Workflow name to check")
    parser.add_argument("--backup-dir", default="./backups", help="Local backup directory")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()
    
    result = analyze_operational_continuity(
        repo=args.repo,
        workflow_name=args.workflow,
        backup_dir=args.backup_dir
    )
    
    output = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)
