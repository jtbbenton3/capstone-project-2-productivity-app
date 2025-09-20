import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import * as api from "../api";

export default function Login({ onLoggedIn }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.login(email, password);
      await onLoggedIn();
      navigate("/");
    } catch (err) {
      setError(err.message || "Login failed");
    }
  }

  return (
    <main style={{ padding: 16 }}>
      <h2>Log in</h2>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: 8, maxWidth: 360 }}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          type="password"
        />
        <button type="submit">Login</button>
        {error && <div style={{ color: "crimson" }}>{error}</div>}
      </form>
      <p>
        Need an account? <Link to="/signup">Sign up</Link>
      </p>
    </main>
  );
}