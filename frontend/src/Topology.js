import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

function Topology({ routers, links, onRouterClick, onCreateLink }) {
  const cyRef = useRef(null);
  const [cy, setCy] = useState(null);
  const [selectedRouter, setSelectedRouter] = useState(null);
  const [connectMode, setConnectMode] = useState(false);
  const [firstSelected, setFirstSelected] = useState(null);
  const [selectedLink, setSelectedLink] = useState(null);

  // Initialize Cytoscape once
  useEffect(() => {
    if (!cyRef.current) return;
    if (cy) return; // Already initialized

    const cytoscapeInstance = cytoscape({
      container: cyRef.current,

      style: [
        // Node styles
        {
          selector: 'node',
          style: {
            'background-color': '#6b7280',
            'label': 'data(label)',
            'color': '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'width': 60,
            'height': 60,
            'border-width': 3,
            'border-color': '#374151',
          }
        },
        // Running routers - green
        {
          selector: 'node[state="running"]',
          style: {
            'background-color': '#10b981',
            'border-color': '#059669',
          }
        },
        // Starting routers - blue
        {
          selector: 'node[state="starting"]',
          style: {
            'background-color': '#3b82f6',
            'border-color': '#2563eb',
          }
        },
        // Stopping routers - yellow
        {
          selector: 'node[state="stopping"]',
          style: {
            'background-color': '#f59e0b',
            'border-color': '#d97706',
          }
        },
        // Stopped routers - gray
        {
          selector: 'node[state="shut off"], node[state="shutoff"]',
          style: {
            'background-color': '#6b7280',
            'border-color': '#4b5563',
          }
        },
        // Selected node in connect mode
        {
          selector: 'node.connect-selected',
          style: {
            'border-width': 5,
            'border-color': '#3b82f6',
          }
        },
        // Selected node
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#10b981',
          }
        },
        // Default edge style (comes FIRST)
        {
          selector: 'edge',
          style: {
            'width': 3,
            'line-color': '#6b7280',
            'target-arrow-color': '#6b7280',
            'target-arrow-shape': 'none',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '9px',
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
            'color': '#9ca3af',
            'text-background-color': '#1f2937',
            'text-background-opacity': 0.8,
            'text-background-padding': '2px',
          }
        },
        // Edge styles - UP links (GREEN - solid line)
        {
          selector: 'edge[status="up"]',
          style: {
            'width': 4,
            'line-color': '#10b981',
            'target-arrow-color': '#10b981',
            'target-arrow-shape': 'none',
            'curve-style': 'bezier',
            'line-style': 'solid',
            'color': '#10b981',
          }
        },
        // Edge styles - DOWN links (RED - dashed line)
        {
          selector: 'edge[status="down"]',
          style: {
            'width': 3,
            'line-color': '#ef4444',
            'target-arrow-color': '#ef4444',
            'target-arrow-shape': 'none',
            'curve-style': 'bezier',
            'line-style': 'dashed',
            'color': '#ef4444',
          }
        },
        // Selected edge
        {
          selector: 'edge:selected',
          style: {
            'width': 5,
            'line-color': '#3b82f6',
          }
        },
      ],

      wheelSensitivity: 0.2,
    });

    setCy(cytoscapeInstance);
  }, [cyRef.current]);

  // Create link with interface prompts
  const handleCreateLink = async (sourceRouter, targetRouter) => {
    const sourceInterface = prompt(`Enter source interface for ${sourceRouter}:`, 'ge-0/0/0');
    if (!sourceInterface) return;

    const targetInterface = prompt(`Enter target interface for ${targetRouter}:`, 'ge-0/0/0');
    if (!targetInterface) return;

    if (onCreateLink) {
      onCreateLink({
        source_router: sourceRouter,
        source_interface: sourceInterface,
        target_router: targetRouter,
        target_interface: targetInterface
      });
    }
  };

  // Handle clicks - separate effect that depends on current state
  useEffect(() => {
    if (!cy) return;

    // Remove old handlers
    cy.removeListener('tap');

    // Click handler for nodes
    cy.on('tap', 'node', function(evt) {
      const node = evt.target;
      const routerData = node.data();

      console.log('Node clicked:', routerData.id, 'Connect mode:', connectMode);

      if (connectMode) {
        // Connect mode logic
        if (!firstSelected) {
          // First node selected
          console.log('First node selected:', routerData.id);
          setFirstSelected(routerData);
          node.addClass('connect-selected');
        } else {
          // Second node selected - create link
          console.log('Second node selected:', routerData.id);
          const secondNode = routerData;

          if (firstSelected.id !== secondNode.id) {
            // Different nodes - create link
            handleCreateLink(firstSelected.id, secondNode.id);
          } else {
            console.log('Cannot connect router to itself');
          }

          // Reset
          cy.nodes().removeClass('connect-selected');
          setFirstSelected(null);
          setConnectMode(false);
        }
      } else {
        // Normal mode - show router details
        setSelectedRouter(routerData);
        setSelectedLink(null);
        if (onRouterClick) {
          onRouterClick(routerData);
        }
      }
    });

    // Click handler for edges
    cy.on('tap', 'edge', function(evt) {
      const edge = evt.target;
      const linkData = edge.data();
      setSelectedLink(linkData);
      setSelectedRouter(null);
    });

    // Click on background to deselect
    cy.on('tap', function(evt) {
      if (evt.target === cy) {
        if (!connectMode) {
          setSelectedRouter(null);
          setSelectedLink(null);
        }
      }
    });

    // Cleanup
    return () => {
      if (cy) {
        cy.removeListener('tap');
      }
    };
  }, [cy, connectMode, firstSelected, onRouterClick, onCreateLink]);

  // Update topology when routers or links change
  useEffect(() => {
    if (!cy) return;

    console.log('Updating topology with', routers.length, 'routers and', (links || []).length, 'links');

    // Get current positions to preserve user's layout
    const positions = {};
    cy.nodes().forEach(node => {
      positions[node.id()] = node.position();
    });

    // Clear existing elements
    cy.elements().remove();

    // Add router nodes
    const nodeElements = routers.map(router => ({
      data: {
        id: router.name,
        label: router.name,
        state: router.state,
        memory: router.memory_mb,
        vcpus: router.vcpus,
        router_type: router.router_type,
      }
    }));

    // Add link edges
    const edgeElements = (links || []).map(link => {
      console.log('Adding edge:', link.id, 'status:', link.status);
      return {
        data: {
          id: link.id,
          source: link.source_router,
          target: link.target_router,
          label: `${link.source_interface} ↔ ${link.target_interface}`,
          status: link.status, // Make sure status is set
          source_interface: link.source_interface,
          target_interface: link.target_interface,
        }
      };
    });

    // Add all elements
    cy.add([...nodeElements, ...edgeElements]);

    // Restore positions if they exist, otherwise use layout
    let hasPositions = false;
    cy.nodes().forEach(node => {
      if (positions[node.id()]) {
        node.position(positions[node.id()]);
        hasPositions = true;
      }
    });

    // If no saved positions, use circle layout
    if (!hasPositions && routers.length > 0) {
      cy.layout({
        name: 'circle',
        animate: true,
        animationDuration: 500,
      }).run();
    }

    // Fit view if this is the first time we have routers
    if (routers.length > 0 && !hasPositions) {
      cy.fit(null, 50);
    }
  }, [cy, routers, links]);

  const handleResetLayout = () => {
    if (cy) {
      cy.layout({
        name: 'circle',
        animate: true,
        animationDuration: 500,
      }).run();
    }
  };

  const handleGridLayout = () => {
    if (cy) {
      cy.layout({
        name: 'grid',
        animate: true,
        animationDuration: 500,
        rows: Math.ceil(Math.sqrt(routers.length)),
      }).run();
    }
  };

  const handleFitView = () => {
    if (cy) {
      cy.fit(null, 50);
    }
  };

  const handleToggleConnectMode = () => {
    if (connectMode) {
      // Cancel connect mode
      if (cy) {
        cy.nodes().removeClass('connect-selected');
      }
      setFirstSelected(null);
    }
    setConnectMode(!connectMode);
  };

  return (
    <div className="w-full h-full flex flex-col bg-vrhost-darker">
      {/* Topology Controls */}
      <div className="bg-vrhost-dark border-b border-gray-700 p-4 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <div>
            <h2 className="text-xl font-bold text-white">Network Topology</h2>
            <p className="text-sm text-gray-400">
              {routers.length} router{routers.length !== 1 ? 's' : ''} • {(links || []).length} link{(links || []).length !== 1 ? 's' : ''} • Drag to reposition
            </p>
          </div>

          {/* Status Legend */}
          <div className="flex items-center gap-4 pl-8 border-l border-gray-700">
            <span className="text-xs font-semibold text-gray-400 uppercase">Status:</span>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-xs text-gray-300">Running</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-xs text-gray-300">Starting</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span className="text-xs text-gray-300">Stopping</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-500"></div>
              <span className="text-xs text-gray-300">Stopped</span>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleToggleConnectMode}
            className={`${
              connectMode
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-green-600 hover:bg-green-700'
            } text-white px-4 py-2 rounded text-sm font-semibold transition-colors`}
          >
            {connectMode ? (firstSelected ? '2. Select Target Router' : '1. Select Source Router') : '🔗 Connect Routers'}
          </button>
          <button
            onClick={handleResetLayout}
            className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm font-semibold transition-colors"
          >
            Circle Layout
          </button>
          <button
            onClick={handleGridLayout}
            className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm font-semibold transition-colors"
          >
            Grid Layout
          </button>
          <button
            onClick={handleFitView}
            className="bg-vrhost-primary hover:bg-vrhost-secondary text-white px-4 py-2 rounded text-sm font-semibold transition-colors"
          >
            Fit View
          </button>
        </div>
      </div>

      {/* Topology Canvas */}
      <div className="flex-1 relative">
        <div ref={cyRef} className="absolute inset-0" />

        {/* Connect Mode Instructions */}
        {connectMode && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-blue-600 border border-blue-500 rounded-lg px-6 py-3">
            <p className="text-white font-semibold">
              {firstSelected
                ? `Selected: ${firstSelected.id} → Click target router to create link`
                : 'Click a router to start creating a connection'}
            </p>
          </div>
        )}

        {/* Selected Router Info */}
        {selectedRouter && !connectMode && (
          <div className="absolute top-4 right-4 bg-vrhost-dark border border-gray-700 rounded-lg p-4 w-64">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-bold text-white">{selectedRouter.label}</h3>
              <button
                onClick={() => setSelectedRouter(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">State:</span>
                <span className={`font-semibold ${
                  selectedRouter.state === 'running' ? 'text-green-400' :
                  selectedRouter.state === 'starting' ? 'text-blue-400' :
                  selectedRouter.state === 'stopping' ? 'text-yellow-400' :
                  'text-gray-400'
                }`}>
                  {selectedRouter.state}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Type:</span>
                <span className="text-white">{selectedRouter.router_type || 'juniper'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Memory:</span>
                <span className="text-white">{selectedRouter.memory} MB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">vCPUs:</span>
                <span className="text-white">{selectedRouter.vcpus}</span>
              </div>
            </div>
          </div>
        )}

        {/* Selected Link Info */}
        {selectedLink && !connectMode && (
          <div className="absolute top-4 right-4 bg-vrhost-dark border border-gray-700 rounded-lg p-4 w-64">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-bold text-white">Link Details</h3>
              <button
                onClick={() => setSelectedLink(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Status:</span>
                <span className={`font-semibold ${
                  selectedLink.status === 'up' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {selectedLink.status}
                </span>
              </div>
              <div className="pt-2 border-t border-gray-700">
                <div className="text-gray-400 mb-1">Source:</div>
                <div className="text-white">{selectedLink.source}</div>
                <div className="text-gray-400 text-xs">{selectedLink.source_interface}</div>
              </div>
              <div className="pt-2 border-t border-gray-700">
                <div className="text-gray-400 mb-1">Target:</div>
                <div className="text-white">{selectedLink.target}</div>
                <div className="text-gray-400 text-xs">{selectedLink.target_interface}</div>
              </div>
              <div className="pt-2 border-t border-gray-700">
                <div className="text-gray-400 text-xs">Link ID: {selectedLink.id}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Topology;
