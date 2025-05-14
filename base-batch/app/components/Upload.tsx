"use client";

import { useState, useRef } from "react";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState("");
  const [uploading, setUploading] = useState(false);

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
      console.log("Response:", response);

      if (response.url) {
        setUrl(response.url);
      }
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
    <main className="max-w-[500px] min-h-screen m-auto flex flex-col gap-4 justify-center items-center">
      <input type="file" id="file" ref={inputFile} onChange={handleChange} />
      <button
        className="bg-white text-black p-2 rounded-md"
        disabled={uploading}
        onClick={uploadFile}
      >
        {uploading ? "Uploading..." : "Upload"}
      </button>
      {url && (
        <a href={url} className="underline" target="_blank">
          {url}
        </a>
      )}
    </main>
  );
}
