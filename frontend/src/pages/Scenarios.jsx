import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { getScenarios, compareScenarios, getProducts, simulateScenario } from '../services/api';
import { Play, GitCompare, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

function Scenarios() {
  const [selectedProduct, setSelectedProduct] = useState('');
  const [newPrice, setNewPrice] = useState('');
  const [simulationDays, setSimulationDays] = useState(30);
  const [simulating, setSimulating] = useState(false);
  const [selectedScenarios, setSelectedScenarios] = useState([]);

  const { data: productsData } = useQuery(
    'products-scenarios',
    () => getProducts({ per_page: 100 }).then(res => res.data)
  );

  const { data: scenariosData, refetch } = useQuery(
    'scenarios',
    () => getScenarios({ limit: 50 }).then(res => res.data)
  );

  const { data: comparison } = useQuery(
    ['compare-scenarios', selectedScenarios],
    () => compareScenarios(selectedScenarios).then(res => res.data),
    { enabled: selectedScenarios.length >= 2 }
  );

  const products = productsData?.products || [];
  const scenarios = scenariosData?.scenarios || [];

  const handleSimulate = async () => {
    if (!selectedProduct || !newPrice) {
      alert('Please select a product and enter a price');
      return;
    }

    setSimulating(true);
    try {
      await simulateScenario({
        product_id: parseInt(selectedProduct),
        new_price: parseFloat(newPrice),
        simulation_days: simulationDays
      });
      await refetch();
      setNewPrice('');
      alert('Scenario simulated successfully!');
    } catch (error) {
      alert('Simulation failed: ' + error.response?.data?.error);
    } finally {
      setSimulating(false);
    }
  };

  const toggleScenarioSelection = (id) => {
    setSelectedScenarios(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
  <h1 className="text-3xl font-bold text-gray-100">What-If Scenarios</h1>
        <p className="text-gray-600 mt-1">Simulate and compare pricing strategies</p>
      </div>

      {/* Scenario Creator */}
      <div className="card">
  <h2 className="text-lg font-semibold text-gray-100 mb-4">Create New Scenario</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Product
            </label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="input w-full"
            >
              <option value="">Choose a product...</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name} (${product.current_price})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New Price ($)
            </label>
            <input
              type="number"
              value={newPrice}
              onChange={(e) => setNewPrice(e.target.value)}
              placeholder="0.00"
              step="0.01"
              min="0"
              className="input w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration (days)
            </label>
            <select
              value={simulationDays}
              onChange={(e) => setSimulationDays(Number(e.target.value))}
              className="input w-full"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
          </div>
        </div>
        <button
          onClick={handleSimulate}
          disabled={simulating || !selectedProduct || !newPrice}
          className="btn btn-primary mt-4 flex items-center gap-2"
        >
          <Play className="h-4 w-4" />
          {simulating ? 'Simulating...' : 'Run Simulation'}
        </button>
      </div>

      {/* Scenario Comparison */}
      {selectedScenarios.length >= 2 && comparison && (
        <div className="card bg-blue-50">
          <h2 className="text-lg font-semibold text-gray-100 mb-4">Comparison Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Best for Revenue</p>
              <p className="font-semibold text-gray-100">{comparison.best_for_revenue?.name}</p>
              <p className="text-lg font-bold text-green-600 mt-1">
                +{comparison.best_for_revenue?.revenue?.revenue_change_percent.toFixed(1)}%
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Best for Profit</p>
              <p className="font-semibold text-gray-100">{comparison.best_for_profit?.name}</p>
              <p className="text-lg font-bold text-green-600 mt-1">
                +{comparison.best_for_profit?.profit?.profit_change_percent.toFixed(1)}%
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Best for Volume</p>
              <p className="font-semibold text-gray-100">{comparison.best_for_volume?.name}</p>
              <p className="text-lg font-bold text-blue-600 mt-1">
                +{comparison.best_for_volume?.demand?.quantity_change_percent.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Scenarios List */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
    <h2 className="text-lg font-semibold text-gray-100">Recent Scenarios</h2>
          {selectedScenarios.length >= 2 && (
            <button
              className="btn btn-secondary flex items-center gap-2"
            >
              <GitCompare className="h-4 w-4" />
              Comparing {selectedScenarios.length} scenarios
            </button>
          )}
        </div>

        {scenarios.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Play className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No scenarios yet</p>
            <p className="text-sm mt-2">Create your first what-if scenario above</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th className="w-12">
                    <input
                      type="checkbox"
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedScenarios(scenarios.map(s => s.id));
                        } else {
                          setSelectedScenarios([]);
                        }
                      }}
                      checked={selectedScenarios.length === scenarios.length && scenarios.length > 0}
                      className="rounded"
                    />
                  </th>
                  <th>Scenario</th>
                  <th>Product</th>
                  <th className="text-right">Price Change</th>
                  <th className="text-right">Revenue Impact</th>
                  <th className="text-right">Profit Impact</th>
                  <th className="text-right">Volume Impact</th>
                  <th>Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {scenarios.map((scenario) => (
                  <tr 
                    key={scenario.id}
                    className={selectedScenarios.includes(scenario.id) ? 'bg-blue-50' : ''}
                  >
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedScenarios.includes(scenario.id)}
                        onChange={() => toggleScenarioSelection(scenario.id)}
                        className="rounded"
                      />
                    </td>
                    <td className="font-medium">{scenario.name}</td>
                    <td>{scenario.product_name}</td>
                    <td className={`text-right font-bold ${
                      scenario.pricing.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {scenario.pricing.price_change_percent >= 0 ? '+' : ''}
                      {scenario.pricing.price_change_percent.toFixed(1)}%
                      <div className="text-xs text-gray-500 font-normal">
                        ${scenario.pricing.current_price.toFixed(2)} → ${scenario.pricing.new_price.toFixed(2)}
                      </div>
                    </td>
                    <td className={`text-right font-bold ${
                      scenario.revenue.revenue_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {scenario.revenue.revenue_change_percent >= 0 ? '+' : ''}
                      {scenario.revenue.revenue_change_percent.toFixed(1)}%
                      <div className="text-xs text-gray-500 font-normal">
                        ${scenario.revenue.total_revenue_change.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </div>
                    </td>
                    <td className={`text-right font-bold ${
                      scenario.profit.profit_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {scenario.profit.profit_change_percent >= 0 ? '+' : ''}
                      {scenario.profit.profit_change_percent.toFixed(1)}%
                      <div className="text-xs text-gray-500 font-normal">
                        ${scenario.profit.total_profit_change.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </div>
                    </td>
                    <td className={`text-right font-bold ${
                      scenario.demand.quantity_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {scenario.demand.quantity_change_percent >= 0 ? '+' : ''}
                      {scenario.demand.quantity_change_percent.toFixed(1)}%
                    </td>
                    <td>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        scenario.recommendation?.action === 'Highly Recommended' ? 'bg-green-100 text-green-700' :
                        scenario.recommendation?.action === 'Recommended' ? 'bg-blue-100 text-blue-700' :
                        scenario.recommendation?.action === 'Consider' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {scenario.recommendation?.action || 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Scenarios;
