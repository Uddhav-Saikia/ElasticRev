import React from 'react';
import { useQuery } from 'react-query';
import { getDashboardAnalytics, exportToExcel } from '../services/api';
import { 
  TrendingUp, 
  DollarSign, 
  ShoppingBag, 
  Package,
  Download,
  RefreshCw
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const COLORS = ['#a855f7', '#c026d3', '#e879f9', '#f0abfc', '#d946ef', '#9333ea'];

function StatCard({ title, value, icon: Icon, trend, color = 'primary' }) {
  const colorClasses = {
    primary: 'from-primary-600 to-primary-700',
    green: 'from-emerald-600 to-emerald-700',
    blue: 'from-blue-600 to-blue-700',
    purple: 'from-purple-600 to-purple-700',
  };

  return (
    <div className="stat-card group">
      <div className="flex items-center justify-between relative z-10">
        <div className="flex-1">
          <p className="text-sm font-semibold text-primary-600 dark:text-primary-400 uppercase tracking-wide">{title}</p>
          <p className="text-3xl font-bold text-primary-700 mt-2">
            <span className="dark:text-blue-400">{value}</span>
          </p>
          {trend && (
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              {trend}
            </p>
          )}
        </div>
        <div className={`bg-gradient-to-br ${colorClasses[color]} p-4 rounded-xl shadow-lg group-hover:scale-110 transition-transform duration-300`}>
          <Icon className="h-7 w-7 text-white" />
        </div>
      </div>
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-primary-500/10 to-transparent rounded-full blur-2xl -z-10"></div>
    </div>
  );
}

function Dashboard() {
  const [days, setDays] = React.useState(30);

  const { data: analytics, isLoading, error: analyticsError, refetch } = useQuery(
    ['dashboard', days],
    () => getDashboardAnalytics(days).then(res => res.data),
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  const handleExport = async () => {
    try {
      const response = await exportToExcel({ days });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      link.setAttribute('download', `pricing_strategy_report_${timestamp}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Show success notification
      alert('Report exported successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export report: ' + (error.response?.data?.error || error.message));
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="relative">
          <RefreshCw className="h-12 w-12 animate-spin text-primary-500" />
          <div className="absolute inset-0 blur-xl bg-primary-500/30 animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (analyticsError) {
    console.error('Dashboard analytics error:', {
      message: analyticsError.message,
      status: analyticsError.response?.status,
      data: analyticsError.response?.data
    });
    return (
      <div className="card bg-red-50 text-red-800 p-8">
        <h2 className="text-xl font-bold mb-2">Error Loading Dashboard</h2>
        <p className="mb-4">{analyticsError.response?.data?.error || analyticsError.message || 'Unknown error'}</p>
        <button 
          onClick={() => refetch()}
          className="btn btn-primary"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="card text-center py-12">
        <p className="text-slate-600">No analytics data available</p>
        <button 
          onClick={() => refetch()}
          className="btn btn-primary mt-4"
        >
          Retry
        </button>
      </div>
    );
  }

  const { overall, by_category, elasticity_distribution, top_products } = analytics;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-400 via-accent-400 to-primary-400 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2 text-lg">Dynamic Pricing Analytics Overview</p>
        </div>
        <div className="flex gap-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="input"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={180}>Last 180 days</option>
          </select>
          <button
            onClick={handleExport}
            className="btn btn-primary flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Export Report
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Revenue"
          value={`$${(overall?.total_revenue || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          icon={DollarSign}
          trend={`${days} days`}
          color="green"
        />
        <StatCard
          title="Total Profit"
          value={`$${(overall?.total_profit || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          icon={TrendingUp}
          trend={`${overall?.avg_margin || 0}% margin`}
          color="primary"
        />
        <StatCard
          title="Products Sold"
          value={(overall?.products_sold || 0).toLocaleString()}
          icon={Package}
          trend={`${(overall?.total_quantity || 0).toLocaleString()} units`}
          color="blue"
        />
        <StatCard
          title="Transactions"
          value={(overall?.total_transactions || 0).toLocaleString()}
          icon={ShoppingBag}
          trend={`Avg $${(overall?.total_revenue / overall?.total_transactions || 0).toFixed(2)}`}
          color="purple"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Category Performance */}
        <div className="card">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <BarChart className="h-5 w-5 text-primary-400" />
            Revenue by Category
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={by_category || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis 
                dataKey="category" 
                angle={-45} 
                textAnchor="end" 
                height={100} 
                stroke="#94a3b8"
                style={{ fontSize: '12px' }}
              />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <Tooltip 
                formatter={(value) => `$${value.toLocaleString()}`}
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #475569',
                  borderRadius: '12px',
                  color: '#f1f5f9'
                }}
              />
              <Legend wrapperStyle={{ color: '#94a3b8' }} />
              <Bar dataKey="revenue" fill="url(#colorRevenue)" name="Revenue" radius={[8, 8, 0, 0]} />
              <Bar dataKey="profit" fill="url(#colorProfit)" name="Profit" radius={[8, 8, 0, 0]} />
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#a855f7" stopOpacity={0.6}/>
                </linearGradient>
                <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#10b981" stopOpacity={0.6}/>
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Elasticity Distribution */}
        <div className="card">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary-400" />
            Elasticity Distribution
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={elasticity_distribution || []}
                dataKey="count"
                nameKey="type"
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                label={({ type, count }) => `${type}: ${count}`}
              >
                {(elasticity_distribution || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #475569',
                  borderRadius: '12px',
                  color: '#f1f5f9'
                }}
              />
              <Legend wrapperStyle={{ color: '#94a3b8' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Products */}
      <div className="card">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Package className="h-5 w-5 text-primary-400" />
          Top 10 Products by Revenue
        </h2>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Product Name</th>
                <th className="text-right">Revenue</th>
                <th className="text-right">% of Total</th>
              </tr>
            </thead>
            <tbody>
              {(top_products || []).map((product, index) => (
                <tr key={product.id}>
                  <td className="font-medium">{index + 1}</td>
                  <td>{product.name}</td>
                  <td className="text-right font-medium">
                    ${product.revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="text-right">
                    {((product.revenue / overall?.total_revenue) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
