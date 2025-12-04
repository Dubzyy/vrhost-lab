import React, { useState, useEffect } from 'react';
import { routerAPI, statsAPI, labAPI, consoleAPI } from './services/api';
import Topology from './Topology';

function App() {
  const [labs, setLabs] = useState([]);
  const [selectedLab, setSelectedLab] = useState(null);
  const [routers, setRouters] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showNewLabModal, setShowNewLabModal] = useState(false);
  const [showNewRouterModal, setShowNewRouterModal] = useState(false);
  const [currentView, setCurrentView] = useState('list'); // 'list' or 'topology'
  
  // New Lab form
  const [newLabName, setNewLabName] = useState('');
  const [newLabDesc, setNewLabDesc] = useState('');
  
  // New Router form
  const [newRouterName, setNewRouterName] = useState('');
  const [newRouterIP, setNewRouterIP] = useState('');
  const [newRouterType, setNewRouterType] = useState('vsrx');
  const [newRouterRAM, setNewRouterRAM] = useState(4);
  const [newRouterCPUs, setNewRouterCPUs] = useState(2);
  const [routerCreating, setRouterCreating] = useState(false);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [selectedLab]);

  const loadData = async () => {
    try {
      const [labsRes, statsRes] = await Promise.all([
        labAPI.list(),
        statsAPI.system()
      ]);
      
      setLabs(labsRes.data);
      setStats(statsRes.data);
      
      if (selectedLab) {
        const routersRes = await labAPI.routers(selectedLab);
        setRouters(routersRes.data.routers);
      } else {
        const allRoutersRes = await routerAPI.list();
        setRouters(allRoutersRes.data.routers);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const createLab = async () => {
    if (!newLabName) return;
    try {
      await labAPI.create({ name: newLabName, description: newLabDesc });
      setShowNewLabModal(false);
      setNewLabName('');
      setNewLabDesc('');
      loadData();
    } catch (error) {
      alert('Failed to create lab: ' + error.message);
    }
  };

  const createRouter = async () => {
    if (!newRouterName || !newRouterIP) {
      alert('Please fill in router name and IP address');
      return;
    }

    setRouterCreating(true);
    try {
      await routerAPI.create({
        name: newRouterName,
        ip: newRouterIP,
        router_type: newRouterType,
        ram_gb: newRouterRAM,
        vcpus: newRouterCPUs
      });
      
      setShowNewRouterModal(false);
      setNewRouterName('');
      setNewRouterIP('');
      setNewRouterType('vsrx');
      setNewRouterRAM(4);
      setNewRouterCPUs(2);
      loadData();
      
      alert('Router created successfully! It will take ~90 seconds to boot.');
    } catch (error) {
      alert('Failed to create router: ' + (error.response?.data?.detail || error.message));
    } finally {
      setRouterCreating(false);
    }
  };

  const startLab = async (labName) => {
    try {
      await labAPI.start(labName);
      loadData();
    } catch (error) {
      alert('Failed to start lab: ' + error.message);
    }
  };

  const stopLab = async (labName) => {
    try {
      await labAPI.stop(labName);
      loadData();
    } catch (error) {
      alert('Failed to stop lab: ' + error.message);
    }
  };

  const deleteLab = async (labName) => {
    if (!window.confirm(`Delete lab ${labName}? (Routers will not be deleted)`)) return;
    try {
      await labAPI.delete(labName);
      if (selectedLab === labName) setSelectedLab(null);
      loadData();
    } catch (error) {
      alert('Failed to delete lab: ' + error.message);
    }
  };

  const handleStart = async (name) => {
    try {
      // Optimistically update UI
      setRouters(routers.map(r => 
        r.name === name ? { ...r, state: 'starting' } : r
      ));
      
      await routerAPI.start(name);
      
      // Refresh after 1 second to get actual state
      setTimeout(loadData, 1000);
    } catch (error) {
      alert('Failed to start router: ' + error.message);
      loadData(); // Reload on error
    }
  };

  const handleStop = async (name) => {
    try {
      // Optimistically update UI
      setRouters(routers.map(r => 
        r.name === name ? { ...r, state: 'stopping' } : r
      ));
      
      await routerAPI.stop(name);
      
      // Refresh after 1 second to get actual state
      setTimeout(loadData, 1000);
    } catch (error) {
      alert('Failed to stop router: ' + error.message);
      loadData(); // Reload on error
    }
  };

  const handleDelete = async (name) => {
    if (!window.confirm(`Delete router ${name}?`)) return;
    try {
      await routerAPI.delete(name);
      loadData();
    } catch (error) {
      alert('Failed to delete router: ' + error.message);
    }
  };

  const handleConsole = async (name) => {
    try {
      // Create console session
      const response = await consoleAPI.createSession(name);
      const { port } = response.data;
    
      // Use actual server hostname for SOCKS proxy compatibility
      // When using SSH tunnel, use the Tailscale IP instead of localhost
      let consoleHost = window.location.hostname;
      if (consoleHost === 'localhost' || consoleHost === '127.0.0.1') {
        // Use Tailscale IP for SOCKS proxy
        consoleHost = '100.77.52.108';
      }
    
      const consoleUrl = `http://${consoleHost}:${port}`;
      window.open(consoleUrl, `console-${name}`, 'width=1000,height=600');
    } catch (error) {
      alert('Failed to open console: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Helper function to get state badge styling
  const getStateBadgeClass = (state) => {
    switch(state) {
      case 'running':
        return 'bg-green-500/20 text-green-400';
      case 'starting':
        return 'bg-blue-500/20 text-blue-400 animate-pulse';
      case 'stopping':
        return 'bg-yellow-500/20 text-yellow-400 animate-pulse';
      case 'shut off':
      case 'shutoff':
        return 'bg-gray-500/20 text-gray-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-vrhost-darker flex items-center justify-center">
        <div className="text-2xl text-vrhost-primary">Loading VRHost Lab...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-vrhost-darker">
      <header className="bg-vrhost-dark border-b border-gray-700 shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-vrhost-primary">VRHost Lab</h1>
              <p className="text-gray-400 text-sm">Lightweight network lab platform</p>
            </div>
            <div className="flex gap-4">
              <button 
                onClick={() => setShowNewLabModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                + New Lab
              </button>
              <button 
                onClick={() => setShowNewRouterModal(true)}
                className="bg-vrhost-primary hover:bg-vrhost-secondary text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                + New Router
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-vrhost-dark p-6 rounded-lg border border-gray-700">
              <div className="text-gray-400 text-sm mb-2">Total Labs</div>
              <div className="text-3xl font-bold text-white">{labs.length}</div>
            </div>
            <div className="bg-vrhost-dark p-6 rounded-lg border border-gray-700">
              <div className="text-gray-400 text-sm mb-2">Total Routers</div>
              <div className="text-3xl font-bold text-vrhost-primary">{stats.vms.running} / {stats.vms.total}</div>
            </div>
            <div className="bg-vrhost-dark p-6 rounded-lg border border-gray-700">
              <div className="text-gray-400 text-sm mb-2">Memory Used</div>
              <div className="text-3xl font-bold text-white">{stats.resources.memory_used_mb} MB</div>
              <div className="text-xs text-gray-400 mt-1">
                {stats.resources.memory_available_mb} MB available
              </div>
            </div>
            <div className="bg-vrhost-dark p-6 rounded-lg border border-gray-700">
              <div className="text-gray-400 text-sm mb-2">Disk Usage</div>
              <div className="text-3xl font-bold text-white">{stats.disk.used_percent}%</div>
              <div className="text-xs text-gray-400 mt-1">
                {stats.disk.used_gb} GB / {stats.disk.total_gb} GB
              </div>
            </div>
          </div>
        )}

        {/* View Switcher */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setCurrentView('list')}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
              currentView === 'list'
                ? 'bg-vrhost-primary text-white'
                : 'bg-vrhost-dark text-gray-400 hover:text-white border border-gray-700'
            }`}
          >
            📋 List View
          </button>
          <button
            onClick={() => setCurrentView('topology')}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
              currentView === 'topology'
                ? 'bg-vrhost-primary text-white'
                : 'bg-vrhost-dark text-gray-400 hover:text-white border border-gray-700'
            }`}
          >
            🌐 Topology View
          </button>
        </div>

        {/* List View */}
        {currentView === 'list' && (
          <>
            <div className="bg-vrhost-dark rounded-lg border border-gray-700 overflow-hidden mb-8">
              <div className="p-6 border-b border-gray-700 flex justify-between items-center">
                <h2 className="text-xl font-bold text-white">Labs</h2>
                <button
                  onClick={() => setSelectedLab(null)}
                  className={`px-4 py-2 rounded text-sm font-semibold transition-colors ${
                    !selectedLab ? 'bg-vrhost-primary text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  All Routers
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6">
                {labs.map((lab) => (
                  <div
                    key={lab.name}
                    className={`bg-vrhost-darker p-6 rounded-lg border transition-colors cursor-pointer ${
                      selectedLab === lab.name ? 'border-vrhost-primary' : 'border-gray-700 hover:border-gray-600'
                    }`}
                    onClick={() => setSelectedLab(lab.name)}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-bold text-white">{lab.name}</h3>
                      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-vrhost-primary/20 text-vrhost-primary">
                        {lab.running_count}/{lab.router_count}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mb-4">{lab.description || 'No description'}</p>
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => { e.stopPropagation(); startLab(lab.name); }}
                        className="flex-1 bg-vrhost-primary/20 hover:bg-vrhost-primary/30 text-vrhost-primary px-4 py-2 rounded text-sm font-semibold transition-colors"
                      >
                        Start All
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); stopLab(lab.name); }}
                        className="flex-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 px-4 py-2 rounded text-sm font-semibold transition-colors"
                      >
                        Stop All
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteLab(lab.name); }}
                        className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm font-semibold transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-vrhost-dark rounded-lg border border-gray-700 overflow-hidden">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold text-white">
                  {selectedLab ? `${selectedLab} - Routers` : 'All Routers'}
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
                {routers.map((router) => (
                  <div
                    key={router.name}
                    className="bg-vrhost-darker p-6 rounded-lg border border-gray-700 hover:border-vrhost-primary transition-colors"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-bold text-white">{router.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStateBadgeClass(router.state)}`}>
                        {router.state}
                      </span>
                    </div>
                    <div className="space-y-2 mb-4 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Memory:</span>
                        <span className="text-white">{router.memory_mb} MB</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">vCPUs:</span>
                        <span className="text-white">{router.vcpus}</span>
                      </div>
                      {router.id && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">ID:</span>
                          <span className="text-white">{router.id}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex flex-col gap-2">
                      {/* Top row: Console + Stop/Start */}
                      <div className="flex gap-2">
                        {router.state === 'running' ? (
                          <>
                            <button
                              onClick={() => handleConsole(router.name)}
                              className="flex-1 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 px-4 py-2 rounded text-sm font-semibold transition-colors"
                            >
                              Console
                            </button>
                            <button
                              onClick={() => handleStop(router.name)}
                              className="flex-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 px-4 py-2 rounded text-sm font-semibold transition-colors"
                            >
                              Stop
                            </button>
                          </>
                        ) : router.state === 'stopping' ? (
                          <button
                            disabled
                            className="flex-1 bg-yellow-500/20 text-yellow-400 px-4 py-2 rounded text-sm font-semibold cursor-not-allowed"
                          >
                            Stopping...
                          </button>
                        ) : router.state === 'starting' ? (
                          <button
                            disabled
                            className="flex-1 bg-blue-500/20 text-blue-400 px-4 py-2 rounded text-sm font-semibold cursor-not-allowed"
                          >
                            Starting...
                          </button>
                        ) : (
                          <button
                            onClick={() => handleStart(router.name)}
                            className="flex-1 bg-vrhost-primary/20 hover:bg-vrhost-primary/30 text-vrhost-primary px-4 py-2 rounded text-sm font-semibold transition-colors"
                          >
                            Start
                          </button>
                        )}
                      </div>
                      {/* Bottom row: Delete */}
                      <button
                        onClick={() => handleDelete(router.name)}
                        className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm font-semibold transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Topology View */}
        {currentView === 'topology' && (
          <div className="bg-vrhost-dark rounded-lg border border-gray-700 overflow-hidden" style={{ height: '600px' }}>
            <Topology routers={routers} />
          </div>
        )}
      </div>

      {/* New Lab Modal */}
      {showNewLabModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-vrhost-dark p-8 rounded-lg border border-gray-700 w-full max-w-md">
            <h2 className="text-2xl font-bold text-white mb-6">Create New Lab</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Lab Name</label>
                <input
                  type="text"
                  value={newLabName}
                  onChange={(e) => setNewLabName(e.target.value)}
                  className="w-full bg-vrhost-darker border border-gray-700 rounded px-4 py-2 text-white focus:border-vrhost-primary outline-none"
                  placeholder="jncis-sp-lab"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-2">Description</label>
                <textarea
                  value={newLabDesc}
                  onChange={(e) => setNewLabDesc(e.target.value)}
                  className="w-full bg-vrhost-darker border border-gray-700 rounded px-4 py-2 text-white focus:border-vrhost-primary outline-none"
                  rows="3"
                  placeholder="My JNCIS-SP study lab"
                />
              </div>
              <div className="flex gap-4 mt-6">
                <button
                  onClick={createLab}
                  className="flex-1 bg-vrhost-primary hover:bg-vrhost-secondary text-white px-6 py-2 rounded-lg font-semibold transition-colors"
                >
                  Create Lab
                </button>
                <button
                  onClick={() => setShowNewLabModal(false)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* New Router Modal */}
      {showNewRouterModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-vrhost-dark p-8 rounded-lg border border-gray-700 w-full max-w-lg">
            <h2 className="text-2xl font-bold text-white mb-6">Create New Router</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Router Name *</label>
                <input
                  type="text"
                  value={newRouterName}
                  onChange={(e) => setNewRouterName(e.target.value)}
                  className="w-full bg-vrhost-darker border border-gray-700 rounded px-4 py-2 text-white focus:border-vrhost-primary outline-none"
                  placeholder="jncis-sp-r1"
                />
                <p className="text-xs text-gray-500 mt-1">Tip: Use lab-name prefix (e.g. jncis-sp-r1) to group routers in labs</p>
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-2">IP Address *</label>
                <input
                  type="text"
                  value={newRouterIP}
                  onChange={(e) => setNewRouterIP(e.target.value)}
                  className="w-full bg-vrhost-darker border border-gray-700 rounded px-4 py-2 text-white focus:border-vrhost-primary outline-none"
                  placeholder="10.10.50.13"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-2">Router Type</label>
                <select
                  value={newRouterType}
                  onChange={(e) => setNewRouterType(e.target.value)}
                  className="w-full bg-vrhost-darker border border-gray-700 rounded px-4 py-2 text-white focus:border-vrhost-primary outline-none"
                >
                  <option value="vsrx">vSRX (Juniper)</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">RAM (GB)</label>
                  <input
                    type="number"
                    value={newRouterRAM}
                    onChange={(e) => setNewRouterRAM(parseInt(e.target.value))}
                    className="w-full bg-vrhost-darker border border-gray-700 rounded px-4 py-2 text-white focus:border-vrhost-primary outline-none"
                    min="2"
                    max="32"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-sm mb-2">vCPUs</label>
                  <input
                    type="number"
                    value={newRouterCPUs}
                    onChange={(e) => setNewRouterCPUs(parseInt(e.target.value))}
                    className="w-full bg-vrhost-darker border border-gray-700 rounded px-4 py-2 text-white focus:border-vrhost-primary outline-none"
                    min="1"
                    max="16"
                  />
                </div>
              </div>
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded p-3 text-sm text-yellow-300">
                ⚠️ Router creation takes ~90 seconds. The router will boot automatically after creation.
              </div>
              <div className="flex gap-4 mt-6">
                <button
                  onClick={createRouter}
                  disabled={routerCreating}
                  className="flex-1 bg-vrhost-primary hover:bg-vrhost-secondary text-white px-6 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {routerCreating ? 'Creating...' : 'Create Router'}
                </button>
                <button
                  onClick={() => setShowNewRouterModal(false)}
                  disabled={routerCreating}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
