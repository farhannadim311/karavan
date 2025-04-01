// src/App.js
import React, { useState } from "react";
import LoginForm from "./components/LoginForm";
import SignUpForm from "./components/SignUpForm";
import Dashboard from "./components/Dashboard";
import "./styles.css";

function App() {
  const [user, setUser] = useState(null);
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="container">
      <div className="stars"></div>
      <h1>AI-Powered Camping & Stargazing</h1>
      {!user ? (
        <div>
          {isLogin ? (
            <>
              <LoginForm setUser={setUser} />
              <div className="toggle-form">
                <p>
                  Don't have an account?{" "}
                  <button onClick={() => setIsLogin(false)}>Sign Up</button>
                </p>
              </div>
            </>
          ) : (
            <>
              <SignUpForm setUser={setUser} />
              <div className="toggle-form">
                <p>
                  Already have an account?{" "}
                  <button onClick={() => setIsLogin(true)}>Log In</button>
                </p>
              </div>
            </>
          )}
        </div>
      ) : (
        <Dashboard user={user} setUser={setUser} />
      )}
    </div>
  );
}

export default App;
