import * as api from "../api";

export default function Home({ user, loading, onRefresh }) {
  async function makeProject() {
    await api.createProject("From UI", "demo");
    alert("Project created. Check your server logs/DB.");
  }

  async function doLogout() {
    await api.logout();
    await onRefresh();
  }

  return (
    <main style={{ padding: 16 }}>
      <h2>Home</h2>
      {loading ? (
        <p>Loading…</p>
      ) : user ? (
        <>
          <p>Welcome, {user.username}!</p>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={makeProject}>Create test project</button>
            <button onClick={doLogout}>Log out</button>
          </div>
        </>
      ) : (
        <p>Please log in or sign up.</p>
      )}
    </main>
  );
}