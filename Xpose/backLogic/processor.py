#!/usr/bin/env python3
import sys
import sqlite3
import subprocess
import os
import json
import glob
from pathlib import Path
from datetime import datetime

# Configure paths
BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = BASE_DIR / "xpose.db"
EMAIL_SCRIPT = BASE_DIR / "emailripping"
USERNAME_SCRIPT = BASE_DIR / "usernameripping"
REPORTS_DIR = BASE_DIR / "reports"
USERNAME_REPORTS_DIR = BASE_DIR / "username_reports"
TIMEOUT = 600  # 10 minutes timeout

def get_latest_report(directory, prefix):
    """Find the most recent report file matching the prefix"""
    try:
        files = glob.glob(f"{directory}/{prefix}*.txt")
        if not files:
            return None
        return max(files, key=os.path.getctime)
    except Exception as e:
        print(f"Error finding report in {directory}: {str(e)}")
        return None

def run_osint_tools(email, username, domain):
    """Execute OSINT tools and return report content"""
    try:
        # Create reports directories if they don't exist
        os.makedirs(REPORTS_DIR, exist_ok=True)
        os.makedirs(USERNAME_REPORTS_DIR, exist_ok=True)

        # Generate expected report prefixes
        email_prefix = email[:3].lower()
        username_prefix = username[:3].lower()

        # Run tools
        env = os.environ.copy()
        env.update({
            'XPOSE_EMAIL': email,
            'XPOSE_USERNAME': username,
            'XPOSE_DOMAIN': domain,
            'PYTHONPATH': str(BASE_DIR)
        })

        # Run email tool
        email_result = subprocess.run(
            [str(EMAIL_SCRIPT), email, domain],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            env=env,
            timeout=TIMEOUT
        )

        # Run username tool
        username_result = subprocess.run(
            [str(USERNAME_SCRIPT), username],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            env=env,
            timeout=TIMEOUT
        )

        # Verify execution
        if email_result.returncode != 0:
            print(f"Email tool failed: {email_result.stderr}")
            return None
            
        if username_result.returncode != 0:
            print(f"Username tool failed: {username_result.stderr}")
            return None

        # Find and read the generated reports
        email_report_path = get_latest_report(REPORTS_DIR, email_prefix)
        username_report_path = get_latest_report(USERNAME_REPORTS_DIR, username_prefix)

        if not email_report_path:
            print("Failed to locate email report file")
            return None
            
        if not username_report_path:
            print("Failed to locate username report file")
            return None

        # Read report contents
        with open(email_report_path, 'r') as f:
            email_content = f.read()
            
        with open(username_report_path, 'r') as f:
            username_content = f.read()

        return {
            'email': email_content,
            'username': username_content,
            'email_path': email_report_path,
            'username_path': username_report_path
        }
        
    except subprocess.TimeoutExpired:
        print(f"Tools timed out after {TIMEOUT} seconds")
        return None
    except Exception as e:
        print(f"Tool execution error: {str(e)}")
        return None

def calculate_risk_score(email_report, username_report):
    """Calculate risk score based on report content"""
    risk_score = 0
    
    # Email report analysis
    if email_report:
        if "breach:" in email_report:
            risk_score += 30
        risk_score += email_report.count("registered:") * 2
        
    # Username report analysis
    if username_report:
        risk_score += username_report.count("[+]") * 3
        
    return min(100, risk_score)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: processor.py <scan_id>")
        sys.exit(1)
        
    scan_id = sys.argv[1]
    print(f"Starting processing for scan {scan_id}")
    start_time = datetime.now()
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get scan data including platforms
            cursor.execute('''
            SELECT email, username, domain, platforms
            FROM scans WHERE id = ?
            ''', (scan_id,))
            scan = cursor.fetchone()
            
            if not scan:
                print(f"Error: Scan {scan_id} not found")
                sys.exit(1)
                
            # Run tools and get reports
            reports = run_osint_tools(
                scan['email'],
                scan['username'],
                scan['domain']
            )
            
            # Calculate risk score
            risk_score = calculate_risk_score(
                reports['email'] if reports else None,
                reports['username'] if reports else None
            ) if reports else 0
            
            # Generate recommendations
            recs = []
            if risk_score > 70:
                recs.append("🔴 Change all passwords immediately - critical risk detected")
            elif risk_score > 40:
                recs.append("🟠 Review privacy settings - multiple exposures found")
            
            if scan['platforms'] and "github" in scan['platforms'].lower():
                recs.append("🟡 Check GitHub for sensitive data exposure")
            
            # Update database
            cursor.execute('''
            UPDATE scans SET
                risk_score = ?,
                email_report = ?,
                username_report = ?,
                recommendations = ?,
                processed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (
                risk_score,
                reports['email'] if reports else "Tool execution failed",
                reports['username'] if reports else "Tool execution failed",
                '\n'.join(recs) if recs else "No recommendations",
                scan_id
            ))
            conn.commit()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"Successfully processed scan {scan_id} in {processing_time:.2f} seconds")
            
    except Exception as e:
        print(f"Fatal error processing scan {scan_id}: {str(e)}")
        sys.exit(1)
