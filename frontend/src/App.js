import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Topology from './Topology';

const API_BASE = process.env.REACT_APP_API_URL || 'http://10.10.50.1:8000';

function App() {
  const [routers, setRouters] = useState([]);
  const [stats, setStats] = useState({});
  const [newRouterName, setNewRouterName] = useState('');
  const [newRouterIP, setNewRouterIP] = useState('');
  const [newRouterType, setNewRouterType] = useState('juniper');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchRouters();
    fetchStats();
    const interval = setInterval(() => {
      fetchRouters();
      fetchStats();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchRouters = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/routers`);
      setRouters(response.data.routers || response.data);
    } catch (err) {
      console.error('Failed to fetch devices:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const createRouter = async () => {
    if (!newRouterName.trim()) {
      setError('Device name is required');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post(`${API_BASE}/api/routers`, {
        name: newRouterName,
        ip: newRouterIP || null,
        router_type: newRouterType
      });

      setSuccess(`Device ${newRouterName} created successfully!`);
      setNewRouterName('');
      setNewRouterIP('');
      fetchRouters();

      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create device');
    } finally {
      setLoading(false);
    }
  };

  const deleteRouter = async (name) => {
    if (!window.confirm(`Are you sure you want to delete ${name}?`)) return;

    try {
      await axios.delete(`${API_BASE}/api/routers/${name}`);
      setSuccess(`Device ${name} deleted`);
      fetchRouters();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete device');
    }
  };

  const startRouter = async (name) => {
    try {
      await axios.post(`${API_BASE}/api/routers/${name}/start`);
      fetchRouters();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start device');
    }
  };

  const stopRouter = async (name) => {
    try {
      await axios.post(`${API_BASE}/api/routers/${name}/stop`);
      fetchRouters();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to stop device');
    }
  };

  const restartRouter = async (name) => {
    try {
      await axios.post(`${API_BASE}/api/routers/${name}/restart`);
      fetchRouters();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to restart device');
    }
  };

  const openConsole = async (name) => {
    try {
      // Always create a fresh console session
      const response = await axios.post(`${API_BASE}/api/routers/${name}/console/session`);

      if (response.data.success) {
        const { port } = response.data;
        const consoleUrl = `http://10.10.50.1:${port}`;

        // Open in new tab
        window.open(consoleUrl, '_blank', 'width=1024,height=768');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to open console');
    }
  };

  const getStateColor = (state) => {
    switch (state) {
      case 'running': return 'bg-green-500';
      case 'shutoff': return 'bg-gray-500';
      case 'paused': return 'bg-yellow-500';
      case 'partial': return 'bg-orange-500';
      default: return 'bg-gray-400';
    }
  };

  const getRouterTypeBadge = (routerType) => {
    if (routerType === 'cisco') {
      return { class: 'bg-blue-600', label: 'Cisco Router' };
    } else if (routerType === 'cisco-switch') {
      return { class: 'bg-blue-500', label: 'Cisco Switch' };
    } else if (routerType === 'juniper-switch') {
      return { class: 'bg-green-500', label: 'Juniper Switch' };
    }
    return { class: 'bg-green-600', label: 'Juniper Router' };
  };

  const getDeviceDescription = (routerType) => {
    const descriptions = {
      'juniper': '🟢 Juniper vSRX - 4GB RAM, 2 vCPU, ~90 sec boot',
      'cisco': '🔷 Cisco CSR1000v - 4GB RAM, 2 vCPU, ~3-5 min boot',
      'cisco-switch': '🔹 Cisco IOSvL2 - 2GB RAM, 2 vCPU, ~2-3 min boot, 16 ports',
      'juniper-switch': '🟩 Juniper vQFX - 4GB RAM, 2 vCPU, ~7-10 min boot, 12x 10GbE ports'
    };
    return descriptions[routerType] || '';
  };

  const getBootTimeWarning = (routerType) => {
    const warnings = {
      'cisco': '⚠️ First boot takes 3-5 minutes',
      'cisco-switch': '⚠️ Boot takes 2-3 minutes',
      'juniper-switch': '⚠️ Boot takes 7-10 minutes (2 VMs: RE + PFE)'
    };
    return warnings[routerType];
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">VRHost Lab 🚀</h1>
              <p className="text-gray-400 text-sm mt-1">Multi-Vendor Network Lab Platform</p>
            </div>
            <div className="flex gap-6 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">{stats.running_routers || 0}</div>
                <div className="text-gray-400">Running</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">{stats.total_routers || 0}</div>
                <div className="text-gray-400">Total Devices</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{stats.cpu_percent?.toFixed(1) || 0}%</div>
                <div className="text-gray-400">CPU</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-400">{stats.memory_percent?.toFixed(1) || 0}%</div>
                <div className="text-gray-400">Memory</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Alerts */}
        {error && (
          <div className="mb-6 bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
            {error}
            <button onClick={() => setError('')} className="float-right font-bold">×</button>
          </div>
        )}
        {success && (
          <div className="mb-6 bg-green-900 border border-green-700 text-green-100 px-4 py-3 rounded">
            {success}
            <button onClick={() => setSuccess('')} className="float-right font-bold">×</button>
          </div>
        )}

        {/* Create Device Form */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 mb-8 border border-gray-700">
          <h2 className="text-2xl font-bold mb-4 text-white">Create New Device</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="Device Name (e.g., r1, sw1)"
              value={newRouterName}
              onChange={(e) => setNewRouterName(e.target.value)}
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
            <input
              type="text"
              placeholder="IP Address (optional)"
              value={newRouterIP}
              onChange={(e) => setNewRouterIP(e.target.value)}
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
            <select
              value={newRouterType}
              onChange={(e) => setNewRouterType(e.target.value)}
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
            >
              <optgroup label="Routers">
                <option value="juniper">Juniper vSRX</option>
                <option value="cisco">Cisco CSR1000v</option>
              </optgroup>
              <optgroup label="Switches">
                <option value="cisco-switch">Cisco IOSvL2</option>
                <option value="juniper-switch">Juniper vQFX</option>
              </optgroup>
            </select>
            <button
              onClick={createRouter}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded disabled:bg-gray-600 transition-colors"
            >
              {loading ? 'Creating...' : '+ New Device'}
            </button>
          </div>

          {/* Device Type Description */}
          {newRouterType && (
            <div className="mt-4 p-3 bg-gray-700 rounded border border-gray-600">
              <p className="text-sm text-gray-300">{getDeviceDescription(newRouterType)}</p>
              {getBootTimeWarning(newRouterType) && (
                <p className="text-sm text-yellow-400 mt-1">{getBootTimeWarning(newRouterType)}</p>
              )}
            </div>
          )}
        </div>

        {/* Topology Visualization */}
        <div className="bg-gray-800 rounded-lg shadow-xl mb-8 border border-gray-700" style={{ height: '600px' }}>
          <div className="p-6 pb-0">
            <h2 className="text-2xl font-bold text-white">Network Topology</h2>
          </div>
          <div style={{ height: 'calc(100% - 80px)' }}>
            <Topology routers={routers} />
          </div>
        </div>

        {/* Device List */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 className="text-2xl font-bold mb-4 text-white">Devices</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-300">Name</th>
                  <th className="text-left py-3 px-4 text-gray-300">Type</th>
                  <th className="text-left py-3 px-4 text-gray-300">State</th>
                  <th className="text-left py-3 px-4 text-gray-300">Resources</th>
                  <th className="text-right py-3 px-4 text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {routers.map((router) => {
                  const badge = getRouterTypeBadge(router.router_type);
                  return (
                    <tr key={router.name} className="border-b border-gray-700 hover:bg-gray-750">
                      <td className="py-3 px-4 font-semibold text-white">{router.name}</td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded text-xs font-semibold text-white ${badge.class}`}>
                          {badge.label}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded text-xs font-semibold text-white ${getStateColor(router.state)}`}>
                          {router.state}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-300 text-sm">
                        {router.memory_mb}MB RAM • {router.vcpus} vCPU
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex justify-end gap-2">
                          {router.state === 'running' && (
                            <>
                              <button
                                onClick={() => openConsole(router.name)}
                                className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition-colors"
                              >
                                Console
                              </button>
                              <button
                                onClick={() => stopRouter(router.name)}
                                className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded transition-colors"
                              >
                                Stop
                              </button>
                              <button
                                onClick={() => restartRouter(router.name)}
                                className="px-3 py-1 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded transition-colors"
                              >
                                Restart
                              </button>
                            </>
                          )}
                          {router.state === 'shutoff' && (
                            <button
                              onClick={() => startRouter(router.name)}
                              className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                            >
                              Start
                            </button>
                          )}
                          <button
                            onClick={() => deleteRouter(router.name)}
                            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {routers.length === 0 && (
                  <tr>
                    <td colSpan="5" className="text-center py-8 text-gray-400">
                      No devices created yet. Create your first device above!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-12 py-6">
        <div className="container mx-auto px-6 text-center text-gray-400 text-sm">
          <p>VRHost Lab - Multi-Vendor Network Lab Platform</p>
          <p className="mt-2">
            Supports: Juniper vSRX • Cisco CSR1000v • Cisco IOSvL2 • Juniper vQFX
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
