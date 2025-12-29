#!/usr/bin/env python3
"""
Probe B: Supply Chain Scanner (NIS2 Art. 21.2.d)
Wraps Trivy for vulnerability detection in containers and dependencies.
"""
import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrivyResult:
    """Result from Trivy scan mapped to NIS2 requirements."""
    status: str  # PASS, WARN, FAIL
    critical_count: int
    high_count: int
    evidence: str
    nis2_article: str = "21.2.d"  # Supply Chain Security


def run_trivy_scan(target: str, scan_type: str = "fs") -> Optional[dict]:
    """
    Run Trivy scan and return JSON output.
    
    Args:
        target: Path to scan (directory, image name, etc.)
        scan_type: 'fs' for filesystem, 'image' for container image
    
    Returns:
        Parsed JSON from Trivy, or None if scan fails
    """
    try:
        cmd = [
            "trivy", scan_type, target,
            "--format", "json",
            "--severity", "CRITICAL,HIGH",
            "--quiet"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0 and not result.stdout:
            print(f"Trivy error: {result.stderr}", file=sys.stderr)
            return None
            
        return json.loads(result.stdout) if result.stdout else {"Results": []}
    
    except FileNotFoundError:
        print("Error: Trivy not installed. Install with: brew install trivy", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("Error: Trivy scan timed out after 5 minutes", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing Trivy output: {e}", file=sys.stderr)
        return None


def analyze_results(trivy_output: dict) -> TrivyResult:
    """
    Analyze Trivy JSON output and map to NIS2 compliance status.
    
    NIS2 Art 21.2.d: Supply chain security
    - FAIL: Any CRITICAL CVE found
    - WARN: HIGH CVEs found but no CRITICAL
    - PASS: No HIGH or CRITICAL CVEs
    """
    critical_count = 0
    high_count = 0
    affected_packages = []
    
    for result in trivy_output.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            severity = vuln.get("Severity", "").upper()
            if severity == "CRITICAL":
                critical_count += 1
                pkg_name = vuln.get("PkgName", "unknown")
                if pkg_name not in affected_packages[:5]:  # Limit to 5
                    affected_packages.append(pkg_name)
            elif severity == "HIGH":
                high_count += 1
    
    if critical_count > 0:
        status = "FAIL"
        evidence = f"❌ {critical_count} CRITICAL CVEs in: {', '.join(affected_packages[:3])}"
    elif high_count > 0:
        status = "WARN"
        evidence = f"⚠️ {high_count} HIGH severity CVEs (no CRITICAL)"
    else:
        status = "PASS"
        evidence = "✅ No CRITICAL/HIGH vulnerabilities detected"
    
    return TrivyResult(
        status=status,
        critical_count=critical_count,
        high_count=high_count,
        evidence=evidence
    )


def scan_for_cve(
    filesystem_path: str = ".",
    requirements_file: str = None,
    dockerfile: str = None
) -> dict:
    """
    Main entry point: Scan for vulnerabilities and return NIS2-mapped results.
    
    Returns:
        dict with format: {
            "status": "PASS/WARN/FAIL",
            "evidence": "...",
            "nis2_article": "21.2.d",
            "details": {...}
        }
    """
    # Priority: Dockerfile > requirements.txt > filesystem
    if dockerfile:
        target = dockerfile
        scan_type = "config"
    elif requirements_file:
        target = requirements_file
        scan_type = "fs"
    else:
        target = filesystem_path
        scan_type = "fs"
    
    trivy_output = run_trivy_scan(target, scan_type)
    
    if trivy_output is None:
        return {
            "status": "WARN",
            "evidence": "⚠️ Trivy scan could not run (tool not available)",
            "nis2_article": "21.2.d",
            "details": {"error": "trivy_not_available"}
        }
    
    result = analyze_results(trivy_output)
    
    return {
        "status": result.status,
        "evidence": result.evidence,
        "nis2_article": result.nis2_article,
        "details": {
            "critical_count": result.critical_count,
            "high_count": result.high_count
        }
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NIS2 Supply Chain Scanner (Probe B)")
    parser.add_argument("--path", default=".", help="Path to scan")
    parser.add_argument("--requirements", help="Path to requirements.txt")
    parser.add_argument("--dockerfile", help="Path to Dockerfile")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()
    
    result = scan_for_cve(
        filesystem_path=args.path,
        requirements_file=args.requirements,
        dockerfile=args.dockerfile
    )
    
    output = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)
    
    # Exit code based on status
    sys.exit(0 if result["status"] == "PASS" else (1 if result["status"] == "FAIL" else 0))
