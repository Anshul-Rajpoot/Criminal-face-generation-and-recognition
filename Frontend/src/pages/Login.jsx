import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiUrl } from "../utils/api.js";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch(apiUrl("/api/auth/login"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("role", data.user.role);
        window.dispatchEvent(new Event("authchange"));

        navigate("/");
      } else {
        alert(data.message || "Login failed");
      }
    } catch {
      alert("Server error");
    } finally {
      setLoading(false);
    }
  };

  return (
  <div style={styles.container}>

    {/* LEFT SIDE */}
    <div style={styles.left}>
      <img src="/assets/logo.png" style={styles.logo} alt="logo" />
    </div>

    {/* RIGHT SIDE */}
    <div style={styles.right}>
      <div style={styles.card}>
        <h2 style={styles.title}>Welcome Back 👋</h2>
        <p style={styles.subtitle}>Login to continue</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            required
            onChange={handleChange}
            style={styles.input}
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            required
            onChange={handleChange}
            style={styles.input}
          />

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p style={styles.footer}>
          Don’t have an account?{" "}
          <span onClick={() => navigate("/signup")} style={styles.link}>
            Signup
          </span>
        </p>
      </div>
    </div>

  </div>
);
}
const styles = {
  container: {
    height: "100vh",
    display: "flex",
    background: "linear-gradient(135deg, #0f172a, #1e293b)",
    position: "relative",
    overflow: "hidden",
  },

  /* LEFT SIDE */
  left: {
    flex: 1,
    marginTop: "-10%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "0 px",
    background: "radial-gradient(circle at left, #1e293b, #020617)",
  },

  logo: {
    width: "200%",
    maxWidth: "800px",
    height: "auto",
    filter: "drop-shadow(0 0 20px rgba(99,102,241,0.35))",
  },

  /* RIGHT SIDE */
  right: {
    flex: 1,
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "40px",
    background: "radial-gradient(circle at left, #1e293b, #020617)",
  },

  /* GLOW EFFECT */
  glow: {
    position: "absolute",
    width: "500px",
    height: "500px",
    background: "radial-gradient(circle, #6366f1, transparent)",
    filter: "blur(120px)",
    top: "-100px",
    left: "-100px",
  },

  card: {
    background: "rgba(255,255,255,0.08)",
    backdropFilter: "blur(15px)",
    padding: "40px",
    borderRadius: "20px",
    width: "360px",
    boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
    textAlign: "center",
    border: "1px solid rgba(255,255,255,0.1)",
    zIndex: 1,
  },

  title: {
    marginBottom: "5px",
    color: "#fff",
    fontSize: "24px",
  },

  subtitle: {
    marginBottom: "25px",
    color: "#cbd5f5",
  },

  form: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },

  input: {
    padding: "14px",
    borderRadius: "10px",
    border: "1px solid rgba(255,255,255,0.2)",
    background: "rgba(255,255,255,0.1)",
    color: "#fff",
    fontSize: "14px",
    outline: "none",
  },

  button: {
    padding: "14px",
    borderRadius: "10px",
    border: "none",
    background: "linear-gradient(135deg,#6366f1,#3b82f6)",
    color: "#fff",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: "pointer",
    transition: "0.3s",
  },

  

  footer: {
    marginTop: "20px",
    fontSize: "14px",
    color: "#cbd5f5",
  },

  link: {
    color: "#818cf8",
    cursor: "pointer",
    fontWeight: "bold",
  },
};