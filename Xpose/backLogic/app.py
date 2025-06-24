#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import subprocess
import os
import json
from threading import Thread
from pathlib import Path
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Path configuration
BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = BASE_DIR / "xpose.db"
REPORTS_DIR = BASE_DIR / "reports"
USERNAME_REPORTS_DIR = BASE_DIR / "username_reports"
FRONTEND_DIR = BASE_DIR.parent / "Frontend"

def init_db():
    """Initialize database with proper schema"""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(USERNAME_REPORTS_DIR, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            username TEXT,
            domain TEXT,
            platforms TEXT,
            form_data TEXT,
            risk_score INTEGER,
            email_report TEXT,
            username_report TEXT,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        )
        ''')
        conn.commit()

def async_processor(scan_id):
    """Run processor in background with proper environment"""
    try:
        subprocess.run(
            [sys.executable, str(BASE_DIR/'processor.py'), str(scan_id)],
            check=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': str(BASE_DIR)}
        )
    except subprocess.CalledProcessError as e:
        print(f"Processor failed for scan {scan_id}: {e}")

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission"""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'platforms' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        username = data.get('username', data['email'].split('@')[0])
        domain = data.get('domain', data['email'].split('@')[1])
        form_data_json = json.dumps(data)
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO scans (email, username, domain, platforms, form_data)
            VALUES (?, ?, ?, ?, ?)
            ''', (data['email'], username, domain, 
                 ','.join(data['platforms']), form_data_json))
            scan_id = cursor.lastrowid
            conn.commit()
        
        Thread(target=async_processor, args=(scan_id,)).start()
        
        return jsonify({
            "scan_id": scan_id,
            "status_url": f"/status/{scan_id}",
            "results_url": f"/results/{scan_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status/<int:scan_id>')
def status(scan_id):
    """Check scan status with complete error handling"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, email, risk_score, email_report, username_report, 
                   recommendations, created_at, processed_at, form_data
            FROM scans WHERE id = ?
            ''', (scan_id,))
            result = cursor.fetchone()
            
            if not result:
                return jsonify({
                    "error": "Scan not found",
                    "ready": False
                }), 404
                
            result_dict = dict(result)
            ready = result_dict['processed_at'] is not None
            
            return jsonify({
                "ready": ready,
                "scan_id": result_dict['id'],
                "email": result_dict['email'],
                "score": result_dict['risk_score'] if result_dict['risk_score'] is not None else 0,
                "created_at": result_dict['created_at'],
                "processed_at": result_dict['processed_at'],
                "reports": {
                    "email": result_dict['email_report'],
                    "username": result_dict['username_report']
                },
                "recommendations": result_dict['recommendations'].split('\n') 
                    if result_dict['recommendations'] else [],
                "form_data": json.loads(result_dict['form_data'])
            })
            
    except Exception as e:
        return jsonify({
            "error": f"Error retrieving scan: {str(e)}",
            "ready": False
        }), 500

@app.route('/results/<int:scan_id>')
def serve_results(scan_id):
    """Serve results page"""
    return send_from_directory(str(FRONTEND_DIR), 'results.html')

if __name__ == '__main__':
    import sys
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)