from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from data_sync_manager import DataSyncManager

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app

# Initialize data sync manager
ml_backend_path = os.path.dirname(os.path.abspath(__file__))
flutter_data_path = os.path.join(os.path.dirname(ml_backend_path), 'meropasalapp')
sync_manager = DataSyncManager(ml_backend_path, flutter_data_path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'ML Backend Sync API'
    })

@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    """Sync data from Flutter app to ML backend"""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Create backup before sync
        backup_path = sync_manager.backup_data()
        
        # Extract features
        feature_extraction_success = sync_manager.extract_features_from_transactions()
        
        # Sync all data
        sync_success = sync_manager.sync_all_data()
        
        if sync_success:
            return jsonify({
                'success': True,
                'message': 'Data synced successfully',
                'timestamp': datetime.now().isoformat(),
                'backup_path': backup_path,
                'feature_extraction': feature_extraction_success
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Data sync failed',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Sync error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/process-data', methods=['POST'])
def process_data():
    """Process data and trigger ML pipeline updates"""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Update ML pipeline
        sync_manager.update_pipeline_data()
        
        return jsonify({
            'success': True,
            'message': 'Data processing completed',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Processing error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/extract-features', methods=['POST'])
def extract_features():
    """Extract features from transaction data"""
    try:
        success = sync_manager.extract_features_from_transactions()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Features extracted successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Feature extraction failed',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Feature extraction error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/backup-data', methods=['POST'])
def backup_data():
    """Create a backup of current data"""
    try:
        backup_path = sync_manager.backup_data()
        
        if backup_path:
            return jsonify({
                'success': True,
                'message': 'Backup created successfully',
                'backup_path': backup_path,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Backup creation failed',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Backup error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sync-status', methods=['GET'])
def sync_status():
    """Get sync status and statistics"""
    try:
        # Check if sync report exists
        report_path = os.path.join(ml_backend_path, 'sync_report.json')
        
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                sync_report = json.load(f)
        else:
            sync_report = {'message': 'No sync report available'}
        
        # Get file statistics
        file_stats = {}
        for data_type, filename in sync_manager.csv_files.items():
            file_path = os.path.join(ml_backend_path, filename)
            if os.path.exists(file_path):
                import pandas as pd
                try:
                    df = pd.read_csv(file_path)
                    file_stats[data_type] = {
                        'records': len(df),
                        'last_modified': datetime.fromtimestamp(
                            os.path.getmtime(file_path)
                        ).isoformat()
                    }
                except:
                    file_stats[data_type] = {
                        'records': 0,
                        'last_modified': None,
                        'error': 'Failed to read file'
                    }
            else:
                file_stats[data_type] = {
                    'records': 0,
                    'last_modified': None,
                    'error': 'File not found'
                }
        
        return jsonify({
            'success': True,
            'sync_report': sync_report,
            'file_statistics': file_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Status check error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/auto-sync', methods=['POST'])
def setup_auto_sync():
    """Setup automatic synchronization"""
    try:
        data = request.get_json() if request.is_json else {}
        interval_minutes = data.get('interval_minutes', 5)
        
        sync_manager.setup_automatic_sync(interval_minutes)
        
        return jsonify({
            'success': True,
            'message': f'Automatic sync enabled (every {interval_minutes} minutes)',
            'interval_minutes': interval_minutes,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Auto-sync setup error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("Starting ML Backend Sync API...")
    print(f"ML Backend Path: {ml_backend_path}")
    print(f"Flutter Data Path: {flutter_data_path}")
    
    # Create necessary directories
    os.makedirs(os.path.join(ml_backend_path, 'backups'), exist_ok=True)
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )
