import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import * as api from "../api";

export default function Signup({ onSignedUp }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.signup(username, email, password);
      await onSignedUp();
      navigate("/");
    } catch (err) {
      setError(err.message || "Signup failed");
    }
  }

  return (
    <main style={{ padding: 16 }}>
      <h2>Sign up</h2>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: 8, maxWidth: 360 }}>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          type="password"
        />
        <button type="submit">Create account</button>
        {error && <div style={{ color: "crimson" }}>{error}</div>}
      </form>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </main>
  );
}