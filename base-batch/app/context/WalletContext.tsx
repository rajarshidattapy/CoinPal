"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { ethers } from "ethers";

interface AccountType {
  address?: string;
  balance?: string;
  chainId?: string;
  network?: string;
}

declare global {
  interface Window {
    ethereum: any;
  }
}

interface WalletContextType {
  accountData: AccountType;
  connectWallet: () => Promise<void>;
}

export const WalletContext = createContext<WalletContextType>({
  accountData: {},
  connectWallet: async () => {},
});

export const WalletProvider = ({ children }: { children: ReactNode }) => {
  const [accountData, setAccountData] = useState<AccountType>({});
  console.log("Account Data: ", accountData);
  const connectWallet = useCallback(async () => {
    if (!window.ethereum) {
      alert("MetaMask not installed");
      return;
    }

    try {
      await window.ethereum.request({
        method: "wallet_requestPermissions",
        params: [{ eth_accounts: {} }],
      });

      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
      });

      if (accounts.length === 0) {
        console.log("No authorized accounts found");
        return;
      }

      const address = accounts[0];
      const provider = new ethers.BrowserProvider(window.ethereum);
      const balance = await provider.getBalance(address);
      const network = await provider.getNetwork();

      setAccountData({
        address,
        balance: ethers.formatEther(balance),
        chainId: network.chainId.toString(),
        network: network.name,
      });

      console.log("Connected to MetaMask:", address);
    } catch (error) {
      console.error("Error connecting to MetaMask:", error);
    }
  }, []);

  return (
    <WalletContext.Provider value={{ accountData, connectWallet }}>
      {children}
    </WalletContext.Provider>
  );
};
export const useWallet = () => {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error("useWallet must be used within a WalletProvider");
  }
  return context;
};
