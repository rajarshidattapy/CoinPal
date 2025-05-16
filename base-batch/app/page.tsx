"use client";

import ConnectWallet from "./components/ConnectWallet";
import Kyc from "./components/Kyc"; // Your friend's KYC component

// --- NEW IMPORTS ---
import PortfolioInsightsDisplay from "./components/insights"; // Assuming insights.tsx is in components/
import { useAccount } from "wagmi"; // Or the OnchainKit equivalent to get connection status

export default function HomePage() {
  // Renamed for clarity
  const { isConnected } = useAccount(); // Hook to check if wallet is connected

  return (
    <div className="flex flex-col min-h-screen font-sans dark:bg-background dark:text-white bg-white text-black">
      <header className="pt-4 pr-4">
        <div className="flex justify-end">
          <div className="wallet-container">
            <ConnectWallet />
          </div>
        </div>
      </header>

      <main className="flex-grow p-4 md:p-6 lg:p-8">
        {" "}
        {/* Added a main content area */}
        {/* Render KYC component if needed, perhaps based on some state */}
        <Kyc />
        {/* --- RENDER PORTFOLIO INSIGHTS --- */}
        <div className="mt-8">
          {/* Add some spacing */}
          {isConnected ? (
            <PortfolioInsightsDisplay />
          ) : (
            <div className="text-center py-10">
              <h2 className="text-2xl font-semibold mb-4">
                Portfolio Insights
              </h2>
              <p>
                Please connect your wallet to view your personalized portfolio
                analysis.
              </p>
              {/* You might want to put another <ConnectWallet /> button here for convenience if the header one is small */}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
