import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { restoreAuth } from "./store/authStore";

restoreAuth();

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);