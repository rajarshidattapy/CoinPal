"use client";

import { useState, useRef } from "react";
import { useUpload } from "../context/Context";

export default function Upload() {
  const [file, setFile] = useState(null);
  // const [url, setUrl] = useState("");
  const [uploading, setUploading] = useState(false);
  const { setUploadUrl, uploadUrl } = useUpload();
  const inputFile = useRef(null);

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      const uploadRequest = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadRequest.ok) {
        throw new Error("Failed to upload file");
      }

      const response = await uploadRequest.json();
      // console.log("Response:", response);

      setUploadUrl(response.url);
      setUploading(false);
    } catch (error) {
      console.error(error);
      setUploading(false);
      alert("Error uploading file");
    }
  };

  const handleChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };

  return (
    <main className="w-full flex flex-col items-start gap-2 p-4 bg-gray-800 rounded-lg border border-gray-700">
      <label htmlFor="file" className="text-sm text-gray-300 mb-1">
        Upload Document:
      </label>
      <input
        type="file"
        id="file"
        ref={inputFile}
        onChange={handleChange}
        className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:bg-blue-600 file:text-white hover:file:bg-blue-700"
      />
      <button
        className="bg-blue-600 text-white px-4 py-2 mt-2 rounded-lg hover:bg-blue-700 transition duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
        disabled={uploading}
        onClick={uploadFile}
      >
        {uploading ? "Uploading..." : "Upload"}
      </button>
      {uploadUrl && (
        <a
          href={uploadUrl}
          className="mt-2 text-blue-500 underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          View Uploaded File
        </a>
      )}
    </main>
  );
}
