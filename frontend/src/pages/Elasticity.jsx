import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { getProducts, bulkCalculateElasticity } from '../services/api';
import { Calculator, TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

function Elasticity() {
  const [calculating, setCalculating] = useState(false);
  const [progress, setProgress] = useState(null);

  const { data: productsData, refetch } = useQuery(
    ['products-with-elasticity'],
    () => getProducts({ per_page: 100 }).then(res => res.data)
  );

  const products = productsData?.products || [];

  const handleBulkCalculate = async () => {
    if (!confirm('Calculate elasticity for all products? This may take a few minutes.')) {
      return;
    }

    setCalculating(true);
    try {
      const result = await bulkCalculateElasticity({});
      setProgress(result.data);
      alert(`Calculation complete! ${result.data.total_calculated} products analyzed`);
      await refetch();
    } catch (error) {
      alert('Bulk calculation failed: ' + error.response?.data?.error);
    } finally {
      setCalculating(false);
    }
  };

  const getElasticityIcon = (type) => {
    switch (type) {
      case 'elastic':
      case 'highly_elastic':
        return <TrendingDown className="h-5 w-5 text-red-500" />;
      case 'inelastic':
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'unit_elastic':
        return <Minus className="h-5 w-5 text-yellow-500" />;
      default:
        return null;
    }
  };

  const getElasticityColor = (coefficient) => {
    const abs = Math.abs(coefficient);
    if (abs > 1.5) return 'text-red-600';
    if (abs > 1) return 'text-orange-600';
    if (abs >= 0.9) return 'text-yellow-600';
    return 'text-green-600';
  };

  const elasticProducts = products.filter(p => p.elasticity);
  const inelasticCount = elasticProducts.filter(p => 
    p.elasticity?.elasticity_type === 'inelastic'
  ).length;
  const elasticCount = elasticProducts.filter(p => 
    ['elastic', 'highly_elastic'].includes(p.elasticity?.elasticity_type)
  ).length;
  const unitElasticCount = elasticProducts.filter(p => 
    p.elasticity?.elasticity_type === 'unit_elastic'
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Price Elasticity</h1>
          <p className="text-gray-600 mt-1">Analyze demand sensitivity to price changes</p>
        </div>
        <button
          onClick={handleBulkCalculate}
          disabled={calculating}
          className="btn btn-primary flex items-center gap-2"
        >
          {calculating ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Calculator className="h-4 w-4" />
          )}
          {calculating ? 'Calculating...' : 'Calculate All'}
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <p className="text-sm text-gray-600">Products Analyzed</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{elasticProducts.length}</p>
          <p className="text-sm text-gray-500 mt-1">of {products.length} total</p>
        </div>
        <div className="card bg-green-50">
          <p className="text-sm text-gray-600">Inelastic</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{inelasticCount}</p>
          <p className="text-sm text-gray-500 mt-1">Price insensitive</p>
        </div>
        <div className="card bg-red-50">
          <p className="text-sm text-gray-600">Elastic</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{elasticCount}</p>
          <p className="text-sm text-gray-500 mt-1">Price sensitive</p>
        </div>
        <div className="card bg-yellow-50">
          <p className="text-sm text-gray-600">Unit Elastic</p>
          <p className="text-3xl font-bold text-yellow-600 mt-2">{unitElasticCount}</p>
          <p className="text-sm text-gray-500 mt-1">Balanced</p>
        </div>
      </div>

      {/* Progress */}
      {progress && (
        <div className="card bg-blue-50">
          <h3 className="font-semibold text-gray-900 mb-2">Calculation Results</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Successful:</span>
              <span className="ml-2 font-medium text-green-600">{progress.total_calculated}</span>
            </div>
            <div>
              <span className="text-gray-600">Errors:</span>
              <span className="ml-2 font-medium text-red-600">{progress.total_errors}</span>
            </div>
          </div>
        </div>
      )}

      {/* Products Table */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Product Elasticity Analysis</h2>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Category</th>
                <th>Price</th>
                <th className="text-center">Type</th>
                <th className="text-right">Coefficient</th>
                <th className="text-right">R²</th>
                <th className="text-right">Optimal Price</th>
                <th className="text-right">Revenue Impact</th>
                <th>Action</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {elasticProducts.length === 0 ? (
                <tr>
                  <td colSpan="10" className="text-center py-8 text-gray-500">
                    No elasticity data available. Click "Calculate All" to analyze products.
                  </td>
                </tr>
              ) : (
                elasticProducts.map((product) => {
                  const elasticity = product.elasticity;
                  return (
                    <tr key={product.id}>
                      <td className="font-medium">{product.name}</td>
                      <td>{product.category}</td>
                      <td className="font-medium">${product.current_price}</td>
                      <td className="text-center">
                        <div className="flex items-center justify-center gap-2">
                          {getElasticityIcon(elasticity.elasticity_type)}
                          <span className="text-xs">{elasticity.elasticity_type}</span>
                        </div>
                      </td>
                      <td className={`text-right font-bold ${getElasticityColor(elasticity.elasticity_coefficient)}`}>
                        {elasticity.elasticity_coefficient.toFixed(3)}
                      </td>
                      <td className="text-right">
                        {elasticity.r_squared ? elasticity.r_squared.toFixed(3) : 'N/A'}
                      </td>
                      <td className="text-right font-medium text-primary-600">
                        ${elasticity.optimal_price || 'N/A'}
                      </td>
                      <td className={`text-right font-medium ${
                        (elasticity.expected_revenue_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {elasticity.expected_revenue_change >= 0 ? '+' : ''}
                        {elasticity.expected_revenue_change?.toFixed(1) || 'N/A'}%
                      </td>
                      <td>
                        <span className="text-xs px-2 py-1 rounded-full bg-gray-100">
                          {elasticity.recommended_action || 'N/A'}
                        </span>
                      </td>
                      <td>
                        <Link
                          to={`/products/${product.id}`}
                          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                        >
                          Details →
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Explanation */}
      <div className="card bg-blue-50">
        <h3 className="font-semibold text-gray-900 mb-3">Understanding Price Elasticity</h3>
        <div className="space-y-2 text-sm text-gray-700">
          <p>
            <strong>Elasticity Coefficient:</strong> Measures % change in quantity demanded per 1% change in price
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
            <div className="bg-white p-3 rounded">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <strong className="text-green-600">Inelastic (|e| &lt; 1)</strong>
              </div>
              <p className="text-xs">Demand insensitive to price. Increase prices to boost revenue.</p>
            </div>
            <div className="bg-white p-3 rounded">
              <div className="flex items-center gap-2 mb-2">
                <TrendingDown className="h-4 w-4 text-red-600" />
                <strong className="text-red-600">Elastic (|e| &gt; 1)</strong>
              </div>
              <p className="text-xs">Demand sensitive to price. Lower prices to increase volume and revenue.</p>
            </div>
            <div className="bg-white p-3 rounded">
              <div className="flex items-center gap-2 mb-2">
                <Minus className="h-4 w-4 text-yellow-600" />
                <strong className="text-yellow-600">Unit Elastic (|e| ≈ 1)</strong>
              </div>
              <p className="text-xs">Revenue unchanged by price changes. Focus on volume or margins.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Elasticity;
