import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation } from 'react-query';
import {
  getProduct,
  getSalesSummary,
  getProductElasticity,
  calculateElasticity,
  getElasticityCurve,
  simulateScenario
} from '../services/api';
import {
  ArrowLeft,
  TrendingUp,
  DollarSign,
  Package,
  Calculator,
  RefreshCw
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

function ProductDetail() {
  const { id } = useParams();
  const [calculating, setCalculating] = useState(false);
  const [simulationPrice, setSimulationPrice] = useState('');
  const [simulationResult, setSimulationResult] = useState(null);

  const { data: product, isLoading: productLoading, error: productError } = useQuery(
    ['product', id],
    () => getProduct(id).then(res => res.data),
    { retry: false }
  );

  const { data: salesSummary, error: salesError } = useQuery(
    ['sales-summary', id],
    () => getSalesSummary({ product_id: id, days: 90 }).then(res => res.data),
    { enabled: !!id, retry: false }
  );

  const { data: elasticity, refetch: refetchElasticity, error: elasticityError } = useQuery(
    ['elasticity', id],
    () => getProductElasticity(id).then(res => res.data).catch(err => {
      // If 404, return null instead of throwing
      if (err.response?.status === 404) {
        return null;
      }
      throw err;
    }),
    { enabled: !!product, retry: false }
  );

  const { data: curveData, error: curveError } = useQuery(
    ['elasticity-curve', id],
    () => getElasticityCurve(id).then(res => res.data).catch(err => {
      // If 404 or no elasticity, return null instead of throwing
      if (err.response?.status === 404) {
        return null;
      }
      throw err;
    }),
    { enabled: !!elasticity, retry: false }
  );

  // Move handlers up here (before early returns cause issues)
  const handleCalculateElasticity = async () => {
    setCalculating(true);
    try {
      await calculateElasticity({
        product_id: parseInt(id),
        model_type: 'gradient_boosting'
      });
      await refetchElasticity();
      alert('Elasticity calculated successfully!');
    } catch (error) {
      alert('Failed to calculate elasticity: ' + error.response?.data?.error);
    } finally {
      setCalculating(false);
    }
  };

  const handleSimulate = async () => {
    if (!simulationPrice || simulationPrice <= 0) {
      alert('Please enter a valid price');
      return;
    }
    try {
      const result = await simulateScenario({
        product_id: parseInt(id),
        new_price: parseFloat(simulationPrice),
        simulation_days: 30
      });
      setSimulationResult(result.data);
    } catch (error) {
      alert('Simulation failed: ' + error.response?.data?.error);
    }
  };

  // Error handling for all queries
  if (productError) {
    console.error('Product API error:', productError);
    return <div className="card text-red-600">Error loading product: {productError.message}</div>;
  }
  if (salesError) {
    console.error('Sales summary API error:', salesError);
  }
  if (elasticityError && elasticityError.response?.status !== 404) {
    console.error('Elasticity API error:', elasticityError);
  }
  if (curveError && curveError.response?.status !== 404) {
    console.error('Elasticity curve API error:', curveError);
  }

  if (productLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!product) {
    return <div className="card">Product not found</div>;
  }

  // Defensive: fallback values for product fields
  let safeProduct = {
    name: '',
    sku: '',
    category: '',
    current_price: 0,
    unit_cost: 0,
    margin: 0,
  };
  if (product) {
    safeProduct = {
      name: product.name || 'N/A',
      sku: product.sku || 'N/A',
      category: product.category || 'N/A',
      current_price: product.current_price ?? 0,
      unit_cost: product.unit_cost ?? 0,
      margin: product.margin ?? 0,
      ...product
    };
  }

  // Defensive: fallback values for salesSummary
  const safeSalesSummary = salesSummary || { total_quantity: 0, total_transactions: 0, total_revenue: 0, total_profit: 0 };

  // Defensive: fallback values for elasticity
  const safeElasticity = elasticity || {
    elasticity_coefficient: 0,
    elasticity_type: 'N/A',
    optimal_price: 0,
    expected_revenue_change: 0,
    recommended_action: '',
  };

  // Defensive: fallback for curveData
  let chartData = [];
  try {
    if (
      curveData &&
      Array.isArray(curveData.prices) &&
      Array.isArray(curveData.quantities) &&
      Array.isArray(curveData.revenues) &&
      Array.isArray(curveData.profits)
    ) {
      chartData = curveData.prices.map((price, i) => ({
        price: price?.toFixed(2) ?? '',
        quantity: curveData.quantities[i]?.toFixed(0) ?? '',
        revenue: curveData.revenues[i]?.toFixed(0) ?? '',
        profit: curveData.profits[i]?.toFixed(0) ?? ''
      }));
    }
  } catch (err) {
    console.error('Error preparing chart data:', err);
    chartData = [];
  }

  // Defensive: fallback for simulationResult
  const safeSimulationResult = simulationResult || {
    revenue: { revenue_change_percent: 0, total_revenue_change: 0 },
    profit: { profit_change_percent: 0, total_profit_change: 0 },
    recommendation: { action: 'N/A', risk_level: 'N/A' },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/products" className="btn btn-secondary">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{safeProduct.name}</h1>
          <p className="text-gray-600 mt-1">{safeProduct.sku} • {safeProduct.category}</p>
        </div>
      </div>

      {/* Product Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <p className="text-sm text-gray-600">Current Price</p>
          <p className="text-2xl font-bold text-primary-600 mt-2">
            ${safeProduct.current_price}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            Cost: ${safeProduct.unit_cost}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Margin</p>
          <p className="text-2xl font-bold text-green-600 mt-2">
            {safeProduct.margin}%
          </p>
          <p className="text-sm text-gray-500 mt-1">
            ${(safeProduct.current_price - safeProduct.unit_cost).toFixed(2)} profit
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Total Sales (90d)</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">
            {safeSalesSummary.total_quantity?.toLocaleString() || 0}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {safeSalesSummary.total_transactions || 0} transactions
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Revenue (90d)</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">
            ${safeSalesSummary.total_revenue?.toLocaleString(undefined, { maximumFractionDigits: 0 }) || 0}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            ${safeSalesSummary.total_profit?.toLocaleString(undefined, { maximumFractionDigits: 0 }) || 0} profit
          </p>
        </div>
      </div>

      {/* Elasticity Section */}
      <div className="card">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Price Elasticity Analysis</h2>
            <p className="text-gray-600 mt-1">Understand how price changes affect demand</p>
          </div>
          <button
            onClick={handleCalculateElasticity}
            disabled={calculating}
            className="btn btn-primary flex items-center gap-2"
          >
            {calculating ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Calculator className="h-4 w-4" />
            )}
            {calculating ? 'Calculating...' : 'Calculate Elasticity'}
          </button>
        </div>

        {elasticity ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Elasticity Coefficient</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">
                  {elasticity.elasticity_coefficient?.toFixed(3)}
                </p>
                <p className="text-sm text-gray-500 mt-1">{elasticity.elasticity_type}</p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Optimal Price</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  ${elasticity.optimal_price}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {((elasticity.optimal_price - safeProduct.current_price) / safeProduct.current_price * 100).toFixed(1)}% change
                </p>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Revenue Impact</p>
                <p className={`text-2xl font-bold mt-1 ${elasticity.expected_revenue_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {elasticity.expected_revenue_change >= 0 ? '+' : ''}
                  {elasticity.expected_revenue_change?.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-500 mt-1">{elasticity.recommended_action}</p>
              </div>
            </div>

            {/* Elasticity Curve */}
            {chartData.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Demand Elasticity Curve</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="price" 
                      label={{ value: 'Price ($)', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis 
                      yAxisId="left"
                      label={{ value: 'Quantity', angle: -90, position: 'insideLeft' }}
                    />
                    <YAxis 
                      yAxisId="right" 
                      orientation="right"
                      label={{ value: 'Revenue ($)', angle: 90, position: 'insideRight' }}
                    />
                    <Tooltip />
                    <Legend />
                    <ReferenceLine
                      yAxisId="left"
                      x={safeProduct.current_price.toFixed(2)}
                      stroke="red"
                      label="Current"
                      strokeDasharray="3 3"
                    />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="quantity"
                      stroke="#0ea5e9"
                      strokeWidth={2}
                      name="Quantity"
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="revenue"
                      stroke="#10b981"
                      strokeWidth={2}
                      name="Revenue"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-600">
            <Calculator className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No elasticity data available</p>
            <p className="text-sm mt-2">Click "Calculate Elasticity" to analyze this product</p>
          </div>
        )}
      </div>

      {/* What-If Simulator */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">What-If Scenario Simulator</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test New Price
            </label>
            <input
              type="number"
              value={simulationPrice}
              onChange={(e) => setSimulationPrice(e.target.value)}
              placeholder={`Current: $${safeProduct.current_price}`}
              step="0.01"
              min="0"
              className="input w-full"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={handleSimulate}
              disabled={!elasticity}
              className="btn btn-primary w-full"
            >
              Simulate
            </button>
          </div>
        </div>

        {simulationResult && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="text-sm text-gray-600">Predicted Revenue Change</p>
              <p className={`text-xl font-bold mt-1 ${simulationResult.revenue.revenue_change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {simulationResult.revenue.revenue_change_percent >= 0 ? '+' : ''}
                {simulationResult.revenue.revenue_change_percent}%
              </p>
              <p className="text-sm text-gray-500">
                ${simulationResult.revenue.total_revenue_change.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Predicted Profit Change</p>
              <p className={`text-xl font-bold mt-1 ${simulationResult.profit.profit_change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {simulationResult.profit.profit_change_percent >= 0 ? '+' : ''}
                {simulationResult.profit.profit_change_percent}%
              </p>
              <p className="text-sm text-gray-500">
                ${simulationResult.profit.total_profit_change.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Recommendation</p>
              <p className="text-xl font-bold mt-1 text-gray-900">
                {simulationResult.recommendation.action}
              </p>
              <p className="text-sm text-gray-500">
                {simulationResult.recommendation.risk_level} risk
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductDetail;
