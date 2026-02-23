import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, TrendingUp, AlertCircle } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import { monitorService, metricsService } from '../services/api';
import toast from 'react-hot-toast';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function MonitorDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [monitor, setMonitor] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [healthChecks, setHealthChecks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMonitorData();
  }, [id]);

  const loadMonitorData = async () => {
    try {
      const [monitorRes, metricsRes, healthRes] = await Promise.all([
        monitorService.getById(id),
        metricsService.getMonitorMetrics(id, 24),
        monitorService.getHealthChecks(id, 24)
      ]);

      setMonitor(monitorRes.data);
      setMetrics(metricsRes.data);
      setHealthChecks(healthRes.data);
    } catch (error) {
      toast.error('Failed to load monitor data');
      navigate('/monitors');
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

  const chartData = {
    labels: healthChecks.slice(0, 20).reverse().map((check) => 
      new Date(check.timestamp).toLocaleTimeString()
    ),
    datasets: [
      {
        label: 'Response Time (ms)',
        data: healthChecks.slice(0, 20).reverse().map((check) => check.response_time_ms),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Response Time (Last 20 Checks)',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/monitors')}
        className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Back to Monitors</span>
      </button>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{monitor.name}</h1>
            <p className="text-gray-600 mt-1">{monitor.url}</p>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            monitor.current_status === 'up' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {monitor.current_status === 'up' ? 'Online' : 'Offline'}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <MetricCard
            title="Uptime"
            value={`${metrics?.uptime_percent?.toFixed(2)}%`}
            icon={<Activity className="w-5 h-5" />}
          />
          <MetricCard
            title="Avg Response"
            value={`${metrics?.avg_response_time_ms?.toFixed(0)}ms`}
            icon={<TrendingUp className="w-5 h-5" />}
          />
          <MetricCard
            title="P95 Response"
            value={`${metrics?.p95_response_time_ms}ms`}
            icon={<TrendingUp className="w-5 h-5" />}
          />
          <MetricCard
            title="Error Rate"
            value={`${metrics?.error_rate?.toFixed(2)}%`}
            icon={<AlertCircle className="w-5 h-5" />}
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Response Time Chart</h2>
        <Line data={chartData} options={chartOptions} />
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Recent Health Checks</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {healthChecks.slice(0, 10).map((check, index) => (
            <div key={index} className="p-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    check.is_up ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(check.timestamp).toLocaleString()}
                    </p>
                    {check.error_message && (
                      <p className="text-sm text-red-600">{check.error_message}</p>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {check.status_code || 'N/A'}
                  </p>
                  <p className="text-sm text-gray-500">
                    {check.response_time_ms}ms
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-600">{title}</span>
        <div className="text-gray-400">{icon}</div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
