"use client";
import { useState } from "react";
import Upload from "./Upload";
import { useUpload } from "../context/Context";
import axios from "axios";
import Locations from "./Locations";

const KycGuide = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const { uploadUrl } = useUpload();

  const handleSubmit = async () => {
    try {
      const res = await axios.post(
        "http://127.0.0.1:3001/api/kyc-guide",
        {
          name: name,
          email: email,
          phone: phone,
          uploadUrl: uploadUrl,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      console.log("Result from api: ", res.data);
    } catch (error) {
      console.error("Error submitting KYC guide:", error);
    }
  };
  return (
    <div className=" flex flex-col justify-center items-center w-full">
      <div className="w-1/2 bg-gray-800 p-8 rounded-2xl shadow-2xl">
        <h2 className="text-3xl font-bold text-white text-center mb-6">
          KYC Verification
        </h2>

        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-300">
              Full Name
            </label>
            <input
              type="text"
              name="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your full name"
              className="w-full p-3 rounded-lg bg-gray-700 text-white placeholder-gray-400 border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 transition duration-200"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-300">Email</label>
            <input
              type="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              className="w-full p-3 rounded-lg bg-gray-700 text-white placeholder-gray-400 border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 transition duration-200"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-300">
              Phone Number
            </label>
            <input
              type="tel"
              name="phone"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Enter your phone number"
              className="w-full p-3 rounded-lg bg-gray-700 text-white placeholder-gray-400 border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 transition duration-200"
            />
          </div>

          <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
            <h3 className="text-lg font-medium text-gray-300 mb-2">
              Document Upload
            </h3>
            <Upload />
          </div>

          <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
            <h3 className="text-lg font-medium text-gray-300 mb-2">
              Location Selection
            </h3>
            <Locations />
          </div>
        </div>

        <button
          onClick={handleSubmit}
          className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 transform hover:scale-105"
        >
          Submit Verification
        </button>
      </div>
    </div>
  );
};

export default KycGuide;
