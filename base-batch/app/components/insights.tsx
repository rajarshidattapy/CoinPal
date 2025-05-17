"use client"; 
import { useState, useEffect } from 'react';
import { useAccount } from 'wagmi'; 

interface AssetDetail {
    asset_id: string;
    name: string;
    quantity: number;
    current_price?: number;
    current_value?: number;
    percentage?: number;
    cost_basis_total?: number;
    unrealized_gain_loss_abs?: number;
    unrealized_gain_loss_percent?: number;
}

interface CompositionDetails {
    user_id: string;
    total_portfolio_value: number;
    asset_composition: AssetDetail[];
    cash_balance: number;
    cash_percentage: number;
    hhi_score?: number;
    risk_metrics?: {
        portfolio_volatility_30d?: number;
        portfolio_beta?: number;
        var_95_confidence_1d?: number;
    };
}

interface FullPortfolioInsightsResponse {
    requested_wallet_address: string;
    data_based_on_mock_user: string;
    portfolio_composition: CompositionDetails;
    historical_performance_summary?: {
        "24h_change_percent"?: number;
        "7d_change_percent"?: number;
        "30d_change_percent"?: number;
        ytd_pnl?: number;
    };
    investment_recommendations: string[];
    global_market_sentiment?: {
        score?: number;
        sentiment?: string;
    };
    asset_specific_news: Record<string, AssetSpecificInsight>;
}

interface ProcessedNewsItem {
    original_headline: string;
    source?: string;
    timestamp?: string;
    llm_summary: string;
    llm_sentiment_label: string;
    llm_analysis?: string;
}

interface AssetSpecificInsight {
    asset_id: string;
    processed_news: ProcessedNewsItem[];
    error?: string | null;
}

const AssetNews: React.FC<{ newsData: AssetSpecificInsight }> = ({ newsData }) => {
  return (
    <div className="space-y-4">
      {newsData.processed_news.map((news: ProcessedNewsItem, index: number) => (
        <div key={index} className="bg-white p-4 rounded-lg shadow">
          <h4 className="font-medium text-lg mb-2">{news.original_headline}</h4>
          <div className="space-y-2 text-sm">
            <p className="text-gray-600">{news.llm_summary}</p>
            <p className="text-gray-700">{news.llm_analysis}</p>
            <div className="flex justify-between items-center mt-2">
              <span className={`px-2 py-1 rounded text-sm ${
                news.llm_sentiment_label.includes('positive') ? 'bg-green-100 text-green-800' :
                news.llm_sentiment_label.includes('negative') ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {news.llm_sentiment_label}
              </span>
              <span className="text-gray-500 text-sm">
                {news.source} • {news.timestamp ? new Date(news.timestamp).toLocaleDateString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default function PortfolioInsightsDisplay() {
  const { address, isConnected } = useAccount(); // Get connected wallet address
  const [insights, setInsights] = useState<FullPortfolioInsightsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInsightsForWallet = async (walletAddress: string) => {
      if (!walletAddress) return;

      setIsLoading(true);
      setError(null);
      setInsights(null); 
      try {
        
        const response = await fetch(`http://localhost:3001/api/v1/portfolio/${walletAddress}/insights`);
        
        if (!response.ok) {
          let errorData;
          try {
            errorData = await response.json();
          } catch {
            errorData = { detail: await response.text() };
          }
          throw new Error(errorData?.detail || errorData?.error || `HTTP error! Status: ${response.status}`);
        }
        
        const data: FullPortfolioInsightsResponse = await response.json();
        setInsights(data);

      } catch (e: unknown) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError("An unknown error occurred while fetching insights.");
        }
        setError(e instanceof Error ? e.message : "An unknown error occurred while fetching insights.");
      } finally {
        setIsLoading(false);
      }
    };

    if (isConnected && address) {
      fetchInsightsForWallet(address);
    } else {
      setInsights(null); 
    }
  }, [isConnected, address]); 
  if (!isConnected || !address) {
    return <div className="p-4 text-center">Please connect your wallet to view portfolio insights.</div>;
  }

  if (isLoading) {
    return <div className="p-4 text-center">Loading portfolio insights...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">Error fetching insights: {error}</div>;
  }

  if (!insights) {
    return <div className="p-4 text-center">No insights available. Try connecting your wallet again or check back later.</div>;
  }

 
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Portfolio Insights for {insights.requested_wallet_address}</h1>
      <p className="text-sm text-gray-500">(Data based on mock user: {insights.data_based_on_mock_user})</p>

      {}
      <section className="p-4 border rounded-lg shadow">
        <h2 className="text-2xl font-semibold mb-3">Portfolio Composition</h2>
        <p><strong>Total Value:</strong> ${insights.portfolio_composition.total_portfolio_value?.toFixed(2)}</p>
        <p><strong>HHI Score:</strong> {insights.portfolio_composition.hhi_score ?? 'N/A'}</p>
        <p><strong>Cash Balance:</strong> ${insights.portfolio_composition.cash_balance?.toFixed(2)} ({insights.portfolio_composition.cash_percentage?.toFixed(2)}%)</p>
        <h3 className="text-xl font-medium mt-4 mb-2">Assets:</h3>
        {insights.portfolio_composition.asset_composition && insights.portfolio_composition.asset_composition.length > 0 ? (
          <ul className="list-disc pl-5 space-y-1">
            {insights.portfolio_composition.asset_composition.map((asset) => (
              <li key={asset.asset_id}>
                <strong>{asset.name} ({asset.asset_id}):</strong> {asset.quantity} units @ ${asset.current_price?.toFixed(2)} = 
                ${asset.current_value?.toFixed(2)} ({asset.percentage?.toFixed(2)}%)
                <br />
                <small className="text-gray-600">
                  Cost Basis: ${asset.cost_basis_total?.toFixed(2) ?? 'N/A'} | 
                  Unrealized P&L: ${asset.unrealized_gain_loss_abs?.toFixed(2) ?? 'N/A'} ({asset.unrealized_gain_loss_percent?.toFixed(2) ?? 'N/A'}%)
                </small>
              </li>
            ))}
          </ul>
        ) : (
          <p>No assets in portfolio.</p>
        )}
      </section>

      {}
      {insights.historical_performance_summary && ( 
        <section className="p-4 border rounded-lg shadow">
            <h2 className="text-2xl font-semibold mb-3">Historical Performance</h2>
            <p>24h Change: {insights.historical_performance_summary['24h_change_percent']?.toFixed(2) ?? 'N/A'}%</p>
            <p>7d Change: {insights.historical_performance_summary['7d_change_percent']?.toFixed(2) ?? 'N/A'}%</p>
            <p>30d Change: {insights.historical_performance_summary['30d_change_percent']?.toFixed(2) ?? 'N/A'}%</p>
            <p>YTD P&L: ${insights.historical_performance_summary.ytd_pnl?.toFixed(2) ?? 'N/A'}</p>
        </section>
      )}
      
      {}
      {insights.portfolio_composition.risk_metrics && ( 
        <section className="p-4 border rounded-lg shadow">
            <h2 className="text-2xl font-semibold mb-3">Risk Metrics (Mocked)</h2>
            <p>30d Volatility: {insights.portfolio_composition.risk_metrics.portfolio_volatility_30d?.toFixed(2) ?? 'N/A'}%</p>
            <p>Beta: {insights.portfolio_composition.risk_metrics.portfolio_beta?.toFixed(2) ?? 'N/A'}</p>
            <p>1-day VaR (95%): ${insights.portfolio_composition.risk_metrics.var_95_confidence_1d?.toFixed(2) ?? 'N/A'}</p>
        </section>
      )}

      {/* Investment Recommendations Section */}
      <section className="p-4 border rounded-lg shadow">
        <h2 className="text-2xl font-semibold mb-3">Investment Recommendations</h2>
        {insights.investment_recommendations && insights.investment_recommendations.length > 0 ? (
          <ul className="list-decimal pl-5 space-y-1">
            {insights.investment_recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        ) : (
          <p>No specific recommendations at this time.</p>
        )}
      </section>

      {/* Global Market Sentiment Section */}
      {insights.global_market_sentiment && (
        <section className="p-4 border rounded-lg shadow">
            <h2 className="text-2xl font-semibold mb-3">Global Market Sentiment</h2>
            <p>Sentiment: {insights.global_market_sentiment.sentiment ?? 'N/A'}</p>
            <p>Score: {insights.global_market_sentiment.score?.toFixed(2) ?? 'N/A'}</p>
        </section>
      )}

      {/* Asset Specific News Section */}
      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">Asset-Specific News & LLM Insights</h2>
        {insights?.asset_specific_news && Object.keys(insights.asset_specific_news).length > 0 ? (
          Object.entries(insights.asset_specific_news).map(([assetId, newsData]) => (
            <div key={assetId} className="mb-6">
              <h3 className="text-xl font-medium mb-3">📰 {assetId} News</h3>
              <AssetNews newsData={newsData} />
            </div>
          ))
        ) : (
          <p className="text-gray-500">No asset-specific news available.</p>
        )}
      </div>
    </div>
  );
}