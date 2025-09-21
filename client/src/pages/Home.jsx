// client/src/pages/Home.jsx
import { Link } from "react-router-dom";
import { useAuth } from "../auth";

export default function Home() {
  const { user } = useAuth();
  return (
    <main style={{ padding: 24 }}>
      <h2>Welcome</h2>
      <p>{user ? `Hi, ${user.username}.` : "You are not signed in."}</p>
      <p>
        {user ? (
          <Link to="/projects">Go to Projects</Link>
        ) : (
          <>
            <Link to="/login">Log in</Link> or <Link to="/signup">Sign up</Link>
          </>
        )}
      </p>
    </main>
  );
}