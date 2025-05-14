"use client";
import React, { useState } from "react";

const Locations = () => {
  const [location, setLocation] = useState(null);

  const fetchLocation = () => {
    fetch("http://localhost:3001/api/check-location", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setLocation(data);
        console.log("Response Data: ", data);

        if (data.is_restricted == false) {
          alert("Coinbase is not restricted in your location");
        } else {
          alert("Coinbase is restricted in your location");
        }
      })
      .catch((err) => {
        console.error("Error Fetching Location: ", err);
      });
  };

  const handleLocationFetch = () => {
    navigator.permissions.query({ name: "geolocation" }).then((permission) => {
      console.log("Current Permission State: ", permission.state);

      if (permission.state === "granted") {
        fetchLocation();
      } else if (permission.state === "prompt") {
        console.log("Prompting for location access...");
        navigator.geolocation.getCurrentPosition(
          fetchLocation,
          (err) => console.error("Geolocation Error: ", err),
          { enableHighAccuracy: true }
        );
      } else {
        alert(
          "Geolocation permission denied. Please enable it in browser settings."
        );
      }
    });
  };

  return (
    <div>
      <h1 className="text-white">Locations</h1>
      <button
        onClick={handleLocationFetch}
        className="bg-blue-500 text-white p-2 rounded"
      >
        Fetch Location
      </button>
    </div>
  );
};

export default Locations;
