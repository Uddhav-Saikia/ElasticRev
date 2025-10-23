import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  TrendingUp, 
  BarChart3, 
  Calculator, 
  ShoppingCart, 
  Settings,
  FileSpreadsheet,
  Menu,
  X,
  Sparkles,
  Zap
} from 'lucide-react';

// Pages
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Elasticity from './pages/Elasticity';
import Scenarios from './pages/Scenarios';
import Recommendations from './pages/Recommendations';

function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/products', label: 'Products', icon: ShoppingCart },
    { path: '/elasticity', label: 'Elasticity', icon: TrendingUp },
    { path: '/scenarios', label: 'Scenarios', icon: Calculator },
    { path: '/recommendations', label: 'Recommendations', icon: Sparkles },
  ];

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="bg-dark-800/60 backdrop-blur-xl border-b border-dark-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center group">
              <div className="relative">
                <Zap className="h-8 w-8 text-primary-500 group-hover:text-primary-400 transition-colors" />
                <div className="absolute inset-0 blur-xl bg-primary-500/30 group-hover:bg-primary-400/40 transition-all -z-10"></div>
              </div>
              <span className="ml-3 text-2xl font-bold bg-gradient-to-r from-primary-400 via-accent-400 to-primary-400 bg-clip-text text-transparent">
                ElasticRev
              </span>
            </div>
            <div className="hidden md:ml-10 md:flex md:space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`relative inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 group ${
                      active
                        ? 'text-white'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {active && (
                      <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-accent-600 rounded-lg opacity-100"></div>
                    )}
                    <Icon className={`h-4 w-4 mr-2 relative z-10 ${active ? '' : 'group-hover:scale-110 transition-transform'}`} />
                    <span className="relative z-10">{item.label}</span>
                    {!active && (
                      <div className="absolute inset-0 bg-dark-700/50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
          
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-700/50 transition-all"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-dark-700/50 bg-dark-800/95 backdrop-blur-xl">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center px-4 py-3 text-base font-medium rounded-lg transition-all ${
                    active
                      ? 'text-white bg-gradient-to-r from-primary-600 to-accent-600'
                      : 'text-gray-400 hover:text-white hover:bg-dark-700/50'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        {/* Animated background gradient */}
        <div className="fixed inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900"></div>
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-600/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>
        
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/products/:id" element={<ProductDetail />} />
            <Route path="/elasticity" element={<Elasticity />} />
            <Route path="/scenarios" element={<Scenarios />} />
            <Route path="/recommendations" element={<Recommendations />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
