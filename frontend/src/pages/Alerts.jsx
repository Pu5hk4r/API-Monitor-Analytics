import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Brain } from 'lucide-react';
import { alertService } from '../services/api';
import toast from 'react-hot-toast';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const response = await alertService.getUserAlerts(100);
      setAlerts(response.data);
    } catch (error) {
      toast.error('Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
        <p className="text-gray-600 mt-1">Monitor alerts and incidents</p>
      </div>

      {alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-medium text-gray-900 mb-2">All systems operational</h3>
          <p className="text-gray-600">No alerts to display</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      )}
    </div>
  );
}

function AlertCard({ alert }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div 
        className="p-6 cursor-pointer hover:bg-gray-50"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className="mt-1">
              {alert.is_resolved ? (
                <CheckCircle className="w-6 h-6 text-green-500" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-red-500" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">
                {alert.monitor_name}
              </h3>
              <p className="text-gray-600 text-sm mb-2">{alert.message}</p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>{new Date(alert.created_at).toLocaleString()}</span>
                <span className={`px-2 py-1 rounded text-xs ${
                  alert.is_resolved 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {alert.is_resolved ? 'Resolved' : 'Active'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {expanded && (
        <div className="px-6 pb-6 border-t border-gray-200 pt-4">
          {alert.details && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-900 mb-2">Details</h4>
              <div className="bg-gray-50 rounded p-3 text-sm space-y-1">
                <p><span className="font-medium">Status Code:</span> {alert.details.status_code || 'N/A'}</p>
                <p><span className="font-medium">Error:</span> {alert.details.error_message || 'N/A'}</p>
                <p><span className="font-medium">URL:</span> {alert.details.url}</p>
              </div>
            </div>
          )}

          {alert.ai_analysis && (
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Brain className="w-5 h-5 text-purple-600" />
                <h4 className="font-medium text-gray-900">AI Analysis</h4>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded p-4 text-sm text-gray-700">
                {alert.ai_analysis}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
