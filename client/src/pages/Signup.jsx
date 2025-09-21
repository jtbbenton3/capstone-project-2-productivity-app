// client/src/pages/Signup.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { user, signup } = useAuth();
  const navigate = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await signup(username.trim(), email.trim(), password);
      navigate("/projects");
    } catch (err) {
      setError(err.message || "Signup failed");
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h2>Sign up</h2>
      <div style={{ marginBottom: 12 }}>
        {user ? `Signed in as ${user.username}` : "Not signed in"}
      </div>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 8, maxWidth: 360 }}>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="username"
          autoComplete="username"
        />
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
          autoComplete="new-password"
        />

        <button type="submit">Create account</button>
        {error && <div style={{ color: "crimson" }}>{error}</div>}
      </form>

      <p style={{ marginTop: 16 }}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </main>
  );
}