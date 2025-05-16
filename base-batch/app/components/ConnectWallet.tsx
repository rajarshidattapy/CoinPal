"use client";
import React, { useState } from "react";
import { useWallet } from "../context/WalletContext";

const ConnectWallet = () => {
  const { accountData, connectWallet } = useWallet();
  const [isLoading, setIsLoading] = useState(false);

  const handleConnect = async () => {
    try {
      setIsLoading(true);
      await connectWallet();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-2">
      <div className="flex items-center gap-2">
        {accountData?.address ? (
          <span className="text-sm font-medium text-green-600">
            Connected as: {accountData.address.slice(0, 6)}...
            {accountData.address.slice(-4)}
          </span>
        ) : (
          <span className="text-sm font-medium text-gray-700">
            Wallet not connected
          </span>
        )}
      </div>

      <button
        onClick={handleConnect}
        className={`px-4 py-2 ${
          isLoading ? "bg-gray-500" : "bg-blue-600 hover:bg-blue-700"
        } 
          text-white font-medium rounded-lg transition-colors duration-200 flex items-center gap-2`}
        disabled={isLoading}
      >
        {isLoading ? (
          <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M6 6V4c0-1.1.9-2 2-2h4a2 2 0 012 2v2h2a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V8c0-1.1.9-2 2-2h2zm4-2h4v2h-4V4z"
              clipRule="evenodd"
            />
          </svg>
        )}
        {isLoading ? "Connecting..." : "Connect Wallet"}
      </button>
    </div>
  );
};

export default ConnectWallet;
