import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { getRecommendations, getCategories } from '../services/api';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, ArrowRight, Download } from 'lucide-react';

function Recommendations() {
  const [category, setCategory] = useState('');

  const { data: recommendationsData, isLoading } = useQuery(
    ['recommendations', category],
    () => getRecommendations({ category }).then(res => res.data)
  );

  const { data: categoriesData } = useQuery(
    'categories-rec',
    () => getCategories().then(res => res.data)
  );

  const recommendations = recommendationsData?.recommendations || [];
  const categories = categoriesData?.categories || [];

  const getActionColor = (action) => {
    if (!action) return 'gray';
    if (action.toLowerCase().includes('increase')) return 'green';
    if (action.toLowerCase().includes('decrease')) return 'blue';
    return 'gray';
  };

  const getActionIcon = (action) => {
    if (!action) return null;
    if (action.toLowerCase().includes('increase')) {
      return <TrendingUp className="h-5 w-5" />;
    }
    return <TrendingDown className="h-5 w-5" />;
  };

  // Group recommendations by action type
  const highImpact = recommendations.filter(r => (r.expected_revenue_change || 0) > 10);
  const mediumImpact = recommendations.filter(r => (r.expected_revenue_change || 0) > 5 && (r.expected_revenue_change || 0) <= 10);
  const lowImpact = recommendations.filter(r => (r.expected_revenue_change || 0) <= 5);

  const handleExportReport = () => {
    // Convert recommendations to CSV format
    const headers = ['Product Name', 'SKU', 'Category', 'Current Price', 'Recommended Price', 'Action', 'Expected Revenue Change', 'Impact Level'];
    const csvContent = [
      headers.join(','),
      ...recommendations.map(rec => [
        `"${rec.product_name || ''}"`,
        rec.sku || '',
        rec.category || '',
        rec.current_price || '',
        rec.recommended_price || '',
        `"${rec.recommended_action || ''}"`,
        `${rec.expected_revenue_change || 0}%`,
        (rec.expected_revenue_change || 0) > 10 ? 'High' : (rec.expected_revenue_change || 0) > 5 ? 'Medium' : 'Low'
      ].join(','))
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `pricing_recommendations_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
  <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Pricing Recommendations</h1>
          <p className="text-slate-400 mt-1">AI-powered optimal pricing strategies</p>
      </div>

      {/* Filter */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Filter by Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="input w-full"
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat.name} value={cat.name}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button 
              onClick={handleExportReport}
              disabled={recommendations.length === 0}
              className="btn btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="h-4 w-4" />
              Export Report
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-red-50">
          <p className="text-sm text-slate-600 dark:text-slate-400">High Impact</p>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">{highImpact.length}</p>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">&gt;10% revenue impact</p>
        </div>
        <div className="card bg-yellow-50">
          <p className="text-sm text-slate-600 dark:text-slate-400">Medium Impact</p>
          <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-2">{mediumImpact.length}</p>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">5-10% revenue impact</p>
        </div>
        <div className="card bg-green-50">
          <p className="text-sm text-slate-600 dark:text-slate-400">Low Impact</p>
          <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">{lowImpact.length}</p>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">&lt;5% revenue impact</p>
        </div>
      </div>

      {isLoading ? (
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-slate-600 mt-4">Loading recommendations...</p>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-slate-600">No recommendations available</p>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
            Calculate elasticity for products first
          </p>
        </div>
      ) : (
        <>
          {/* High Impact Recommendations */}
          {highImpact.length > 0 && (
            <div className="card border-l-4 border-red-500">
              <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-sm">
                  High Priority
                </span>
                  <span className="dark:text-white">High Impact Opportunities</span>
              </h2>
              <div className="space-y-3">
                {highImpact.map((rec) => (
                  <div
                    key={rec.product_id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg bg-${getActionColor(rec.recommended_action)}-100`}>
                          {getActionIcon(rec.recommended_action)}
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900">{rec.product_name}</h3>
                          <p className="text-sm text-slate-600">{rec.category}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-8">
                      <div className="text-right">
                        <p className="text-sm text-slate-600">Current Price</p>
                        <p className="text-lg font-bold text-slate-900">${(rec.current_price ?? 0).toFixed(2)}</p>
                      </div>
                      <ArrowRight className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                      <div className="text-right">
                        <p className="text-sm text-slate-600">Optimal Price</p>
                        <p className="text-lg font-bold text-primary-600">${(rec.optimal_price ?? rec.current_price ?? 0).toFixed(2)}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-slate-600">Expected Impact</p>
                        <p className="text-lg font-bold text-green-600">
                          +{((rec.expected_revenue_change ?? 0).toFixed(1))}%
                        </p>
                      </div>
                      <Link
                        to={`/products/${rec.product_id}`}
                        className="btn btn-primary"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* All Recommendations Table */}
          <div className="card">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">All Recommendations</h2>
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Category</th>
                    <th className="text-right">Current Price</th>
                    <th className="text-right">Optimal Price</th>
                    <th className="text-right">Change</th>
                    <th className="text-center">Elasticity</th>
                    <th>Action</th>
                    <th className="text-right">Impact</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {recommendations.map((rec) => {
                    const priceChange = ((rec.optimal_price - rec.current_price) / rec.current_price) * 100;
                    return (
                      <tr key={rec.product_id}>
                        <td className="font-medium">{rec.product_name}</td>
                        <td>{rec.category}</td>
                        <td className="text-right">${(rec.current_price ?? 0).toFixed(2)}</td>
                        <td className="text-right font-bold text-primary-600">
                          ${(rec.optimal_price ?? rec.current_price ?? 0).toFixed(2)}
                        </td>
                        <td className={`text-right font-bold ${
                          (((rec.optimal_price ?? rec.current_price ?? 0) - (rec.current_price ?? 0)) / (rec.current_price ?? 1)) * 100 >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {(((rec.optimal_price ?? rec.current_price ?? 0) - (rec.current_price ?? 0)) / (rec.current_price ?? 1)) * 100 >= 0 ? '+' : ''}{((((rec.optimal_price ?? rec.current_price ?? 0) - (rec.current_price ?? 0)) / (rec.current_price ?? 1)) * 100).toFixed(1)}%
                        </td>
                        <td className="text-center">
                          <span
                            className={`text-xs px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-700 whitespace-nowrap flex flex-row items-center ${
                              rec.elasticity_type === 'elastic' || rec.elasticity_type === 'highly_elastic'
                                ? 'text-red-600 font-semibold'
                                : rec.elasticity_type === 'inelastic'
                                ? 'text-green-600 font-semibold'
                                : rec.elasticity_type === 'unit_elastic'
                                ? 'text-yellow-600 font-semibold'
                                : 'text-slate-700'
                            }`}
                          >
                            {rec.elasticity_type || 'N/A'}
                          </span>
                          <span
                            className={`text-xs ml-2 font-mono font-semibold ${
                              rec.elasticity_coefficient > 1
                                ? 'text-red-600'
                                : rec.elasticity_coefficient < 1 && rec.elasticity_coefficient !== null && rec.elasticity_coefficient !== undefined
                                ? 'text-green-600'
                                : rec.elasticity_coefficient === 1
                                ? 'text-yellow-600'
                                : 'text-slate-600 dark:text-slate-400'
                            }`}
                          >
                            {rec.elasticity_coefficient ? rec.elasticity_coefficient.toFixed(2) : 'N/A'}
                          </span>
                        </td>
                        <td>
                          <div className="flex items-center gap-2">
                            {getActionIcon(rec.recommended_action)}
                            <span className="text-sm">{rec.recommended_action || 'N/A'}</span>
                          </div>
                        </td>
                        <td className={`text-right font-bold ${
                          (rec.expected_revenue_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {(rec.expected_revenue_change ?? 0) >= 0 ? '+' : ''}
                          {(rec.expected_revenue_change ?? 0).toFixed(1)}%
                        </td>
                        <td>
                          <Link
                            to={`/products/${rec.product_id}`}
                            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                          >
                            Details →
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Recommendations;
