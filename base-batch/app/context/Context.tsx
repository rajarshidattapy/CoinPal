"use client";
import { createContext, useContext, useState, ReactNode } from "react";

interface UploadContextType {
  uploadUrl: string;
  setUploadUrl: (uploadUrl: string) => void;
}
const UploadContext = createContext<UploadContextType | undefined>(undefined);
export const useUpload = () => {
  const context = useContext(UploadContext);
  if (!context) {
    throw new Error("useUpload must be used within an UploadProvider");
  }
  return context;
};
export const UploadProvider = ({ children }: { children: ReactNode }) => {
  const [uploadUrl, setUploadUrl] = useState<string>("");

  return (
    <UploadContext.Provider value={{ uploadUrl, setUploadUrl }}>
      {children}
    </UploadContext.Provider>
  );
};
