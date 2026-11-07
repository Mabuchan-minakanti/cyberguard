
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, Mail, Lock } from "lucide-react";
import "./Login.css";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleLogin(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!email || !password) {
      alert("Please enter your email and password.");
      return;
    }

    // Temporary frontend-only login.
    // Real authentication will be connected to the backend later.
    navigate("/dashboard");
  }

  return (
    <main className="login-page">
      <Link to="/" className="login-brand">
        <ShieldCheck size={30} />
        <span>CyberGuard AI</span>
      </Link>

      <section className="login-card">
        <div className="login-icon"><ShieldCheck size={32} /></div>
        <h1>Welcome back</h1>
        <p>Sign in to access your network security workspace.</p>

        <form onSubmit={handleLogin}>
          <label htmlFor="email">Email address</label>
          <div className="login-input">
            <Mail size={18} />
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <label htmlFor="password">Password</label>
          <div className="login-input">
            <Lock size={18} />
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="login-options">
            <Link to="/forgot-password">Forgot password?</Link>
          </div>

          <button className="login-submit" type="submit">
            Sign In
          </button>
        </form>

        <div className="login-footer">
          Don't have an account? <Link to="/register">Create account</Link>
        </div>
      </section>
    </main>
  );
}

export default Login;
