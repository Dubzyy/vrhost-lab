import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

function Topology({ routers, onRouterClick }) {
  const cyRef = useRef(null);
  const [cy, setCy] = useState(null);
  const [selectedRouter, setSelectedRouter] = useState(null);

  useEffect(() => {
    if (!cyRef.current || cy) return;

    // Initialize Cytoscape
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
        // Selected node
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#10b981',
          }
        },
        // Edge styles (connections between routers)
        {
          selector: 'edge',
          style: {
            'width': 3,
            'line-color': '#4b5563',
            'target-arrow-color': '#4b5563',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          }
        },
      ],

      layout: {
        name: 'circle',
        animate: true,
        animationDuration: 500,
      },

      wheelSensitivity: 0.2,
    });

    // Click handler
    cytoscapeInstance.on('tap', 'node', function(evt) {
      const node = evt.target;
      const routerData = node.data();
      setSelectedRouter(routerData);
      if (onRouterClick) {
        onRouterClick(routerData);
      }
    });

    setCy(cytoscapeInstance);
  }, [cy, onRouterClick]);

  // Update nodes when routers change
  useEffect(() => {
    if (!cy) return;

    // Get current positions
    const positions = {};
    cy.nodes().forEach(node => {
      positions[node.id()] = node.position();
    });

    // Clear and rebuild
    cy.elements().remove();

    // Add router nodes
    const elements = routers.map(router => ({
      data: {
        id: router.name,
        label: router.name,
        state: router.state,
        memory: router.memory_mb,
        vcpus: router.vcpus,
      }
    }));

    cy.add(elements);

    // Restore positions or use layout
    let hasPositions = false;
    cy.nodes().forEach(node => {
      if (positions[node.id()]) {
        node.position(positions[node.id()]);
        hasPositions = true;
      }
    });

    if (!hasPositions) {
      cy.layout({ name: 'circle', animate: true }).run();
    }
  }, [cy, routers]);

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

  return (
    <div className="w-full h-full flex flex-col bg-vrhost-darker">
      {/* Topology Controls */}
      <div className="bg-vrhost-dark border-b border-gray-700 p-4 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <div>
            <h2 className="text-xl font-bold text-white">Network Topology</h2>
            <p className="text-sm text-gray-400">
              {routers.length} router{routers.length !== 1 ? 's' : ''} • Drag to reposition • Click for details
            </p>
          </div>
          
          {/* Status Legend - Now in header */}
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

        {/* Selected Router Info */}
        {selectedRouter && (
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
      </div>
    </div>
  );
}

export default Topology;
