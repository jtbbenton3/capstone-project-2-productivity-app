// client/src/pages/Login.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { user, login } = useAuth();
  const navigate = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await login(email.trim(), password);
      navigate("/projects");
    } catch (err) {
      setError(err.message || "Login failed");
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h2>Log in</h2>
      <div style={{ marginBottom: 12 }}>
        {user ? `Signed in as ${user.username}` : "Not signed in"}
      </div>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 8, maxWidth: 360 }}>
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="email"
          type="email"
          autoComplete="email"
        />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
          type="password"
          autoComplete="current-password"
        />
        <button type="submit">Login</button>
        {error && <div style={{ color: "crimson" }}>{error}</div>}
      </form>

      <p style={{ marginTop: 16 }}>
        Need an account? <Link to="/signup">Sign up</Link>
      </p>
    </main>
  );
}